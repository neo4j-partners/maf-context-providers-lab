# /// script
# requires-python = ">=3.10"
# dependencies = ["python-dotenv"]
# ///
"""Sync GraphAcademy course content into Antora site structure."""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
import os


# GraphAcademy-specific attributes to strip from AsciiDoc headers
STRIP_ATTRIBUTES = {
    "status",
    "categories",
    "duration",
    "caption",
    "key-points",
    "usecase",
    "type",
    "order",
}


@dataclass
class Question:
    filename: str
    content: str


@dataclass
class Lesson:
    slug: str
    order: int
    title: str
    content: str
    questions: list[Question] = field(default_factory=list)
    images: list[Path] = field(default_factory=list)
    source_dir: Path = field(default_factory=Path)


@dataclass
class Module:
    slug: str
    order: int
    title: str
    content: str
    lessons: list[Lesson] = field(default_factory=list)


@dataclass
class Course:
    title: str
    duration: str
    content: str
    modules: list[Module] = field(default_factory=list)
    root_images: list[Path] = field(default_factory=list)


def load_env() -> Path:
    """Load .env and return validated COURSE_DIRECTORY path."""
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    course_dir = os.environ.get("COURSE_DIRECTORY")
    if not course_dir:
        print("Error: COURSE_DIRECTORY not set in .env")
        sys.exit(1)

    path = Path(course_dir)
    if not path.exists():
        print(f"Error: COURSE_DIRECTORY does not exist: {path}")
        sys.exit(1)

    if not (path / "course.adoc").exists():
        print(f"Error: No course.adoc found in {path}")
        sys.exit(1)

    return path


def extract_title(content: str) -> str:
    """Extract the = Title from AsciiDoc content."""
    for line in content.splitlines():
        if line.startswith("= "):
            return line[2:].strip()
    return "Untitled"


def extract_attribute(content: str, name: str) -> str | None:
    """Extract an :attribute: value from AsciiDoc content."""
    pattern = re.compile(rf"^:{re.escape(name)}:\s*(.*)$", re.MULTILINE)
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def extract_order_from_slug(slug: str) -> int:
    """Extract numeric prefix from a directory slug like '1-introduction'."""
    match = re.match(r"^(\d+)-", slug)
    return int(match.group(1)) if match else 999


def strip_attributes(content: str) -> str:
    """Remove GraphAcademy-specific attribute lines from the header."""
    lines = content.splitlines(keepends=True)
    result = []
    in_header = True

    for line in lines:
        stripped = line.strip()

        # Header ends at first blank line after title/attributes
        if in_header and stripped == "" and len(result) > 1:
            in_header = False
            result.append(line)
            continue

        if in_header:
            # Check if this is an attribute line we should strip
            attr_match = re.match(r"^:([^:]+):", stripped)
            if attr_match and attr_match.group(1) in STRIP_ATTRIBUTES:
                continue

        result.append(line)

    return "".join(result)


def apply_leveloffset(content: str, offset: int) -> str:
    """Shift heading levels by offset (add '=' characters)."""
    if offset <= 0:
        return content

    lines = content.splitlines(keepends=True)
    result = []
    for line in lines:
        if re.match(r"^=+ ", line):
            result.append("=" * offset + line)
        else:
            result.append(line)
    return "".join(result)


def resolve_includes(content: str, lesson_dir: Path) -> str:
    """Inline include::questions/... directives."""
    pattern = re.compile(
        r"^include::questions/([^\[]+)\[([^\]]*)\]\s*$", re.MULTILINE
    )

    def replace_include(match: re.Match) -> str:
        filename = match.group(1)
        attrs = match.group(2)
        question_path = lesson_dir / "questions" / filename

        if not question_path.exists():
            return f"// WARNING: Missing include: questions/{filename}\n"

        question_content = question_path.read_text()

        # Handle leveloffset
        offset_match = re.search(r"leveloffset=\+(\d+)", attrs)
        if offset_match:
            offset = int(offset_match.group(1))
            question_content = apply_leveloffset(question_content, offset)

        return question_content

    return pattern.sub(replace_include, content)


def convert_course_links(content: str) -> str:
    """Convert internal course links to absolute GraphAcademy URLs."""
    return re.sub(
        r"link:/courses/",
        "link:https://graphacademy.neo4j.com/courses/",
        content,
    )


def remove_read_macros(content: str) -> str:
    """Remove read::...[] macros."""
    return re.sub(r"^read::.*\[\]\s*$", "", content, flags=re.MULTILINE)


def remove_ifeval_blocks(content: str) -> str:
    """Remove ifeval::[...]...endif::[] blocks."""
    return re.sub(
        r"^ifeval::.*$\n(.*\n)*?^endif::\[\]\s*$\n?",
        "",
        content,
        flags=re.MULTILINE,
    )


def replace_instance_placeholders(content: str) -> str:
    """Replace {instance-*} placeholders with generic values."""
    replacements = {
        "{instance-ip}": "your-neo4j-host",
        "{instance-boltPort}": "7687",
        "{instance-username}": "neo4j",
        "{instance-password}": "your-password",
        "{instance-database}": "neo4j",
    }
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    # Also remove [copy]# wrappers
    content = re.sub(r"\[copy\]#([^#]*)#", r"\1", content)

    return content


def replace_duration(content: str, duration: str) -> str:
    """Replace {duration} with literal value."""
    return content.replace("{duration}", duration)


def remove_includes_section(content: str) -> str:
    """Remove the [.includes] section from course.adoc."""
    pattern = re.compile(r"^\[\.includes\]\s*$.*", re.MULTILINE | re.DOTALL)
    return pattern.sub("", content).rstrip() + "\n"


def transform_lesson(content: str, lesson_dir: Path, duration: str) -> str:
    """Apply all transformations to a lesson file."""
    content = strip_attributes(content)
    content = resolve_includes(content, lesson_dir)
    content = convert_course_links(content)
    content = remove_read_macros(content)
    content = remove_ifeval_blocks(content)
    content = replace_instance_placeholders(content)
    content = replace_duration(content, duration)
    return content


def transform_module(
    content: str, module_order: int, lessons: list[Lesson], duration: str
) -> str:
    """Apply transformations to a module.adoc file."""
    content = strip_attributes(content)
    content = replace_duration(content, duration)

    # Convert link:./lesson-slug/[text, role=btn] to xref
    def replace_module_link(match: re.Match) -> str:
        lesson_slug = match.group(1)
        text = match.group(2)
        # Find the matching lesson to get the correct page filename
        for lesson in lessons:
            if lesson.slug == lesson_slug:
                page_name = f"{module_order}-{lesson.slug}.adoc"
                return f"xref:{page_name}[{text}]"
        # Fallback: just remove the link
        return text

    content = re.sub(
        r"link:\./([^/]+)/\[([^\],]+)(?:,\s*role=btn)?\]",
        replace_module_link,
        content,
    )

    return content


def transform_course(content: str, duration: str) -> str:
    """Apply transformations to course.adoc for index page."""
    content = strip_attributes(content)
    content = convert_course_links(content)
    content = replace_duration(content, duration)
    content = replace_instance_placeholders(content)
    content = remove_includes_section(content)
    return content


def discover_course(course_dir: Path) -> Course:
    """Walk the course directory and build an ordered data model."""
    course_content = (course_dir / "course.adoc").read_text()
    course_title = extract_title(course_content)
    duration = extract_attribute(course_content, "duration") or "2 hours"

    # Collect root images
    root_images = []
    for img_name in ["banner.png", "illustration.svg"]:
        img_path = course_dir / img_name
        if img_path.exists():
            root_images.append(img_path)

    modules_dir = course_dir / "modules"
    modules = []

    if modules_dir.exists():
        for module_path in sorted(modules_dir.iterdir()):
            if not module_path.is_dir():
                continue

            module_adoc = module_path / "module.adoc"
            if not module_adoc.exists():
                print(f"  Warning: No module.adoc in {module_path.name}, skipping")
                continue

            module_content = module_adoc.read_text()
            module_slug = module_path.name
            module_order = extract_order_from_slug(module_slug)

            # Override with :order: attribute if present
            order_attr = extract_attribute(module_content, "order")
            if order_attr:
                module_order = int(order_attr)

            module_title = extract_title(module_content)

            # Discover lessons
            lessons = []
            lessons_dir = module_path / "lessons"
            if lessons_dir.exists():
                for lesson_path in sorted(lessons_dir.iterdir()):
                    if not lesson_path.is_dir():
                        continue

                    lesson_adoc = lesson_path / "lesson.adoc"
                    if not lesson_adoc.exists():
                        print(
                            f"  Warning: No lesson.adoc in {lesson_path.name}, skipping"
                        )
                        continue

                    lesson_content = lesson_adoc.read_text()
                    lesson_slug = lesson_path.name
                    lesson_order = extract_order_from_slug(lesson_slug)

                    order_attr = extract_attribute(lesson_content, "order")
                    if order_attr:
                        lesson_order = int(order_attr)

                    lesson_title = extract_title(lesson_content)

                    # Discover questions
                    questions = []
                    questions_dir = lesson_path / "questions"
                    if questions_dir.exists():
                        for q_file in sorted(questions_dir.glob("*.adoc")):
                            questions.append(
                                Question(
                                    filename=q_file.name,
                                    content=q_file.read_text(),
                                )
                            )

                    # Discover images
                    images = []
                    images_dir = lesson_path / "images"
                    if images_dir.exists():
                        images = list(images_dir.iterdir())

                    lessons.append(
                        Lesson(
                            slug=lesson_slug,
                            order=lesson_order,
                            title=lesson_title,
                            content=lesson_content,
                            questions=questions,
                            images=images,
                            source_dir=lesson_path,
                        )
                    )

            lessons.sort(key=lambda l: l.order)

            modules.append(
                Module(
                    slug=module_slug,
                    order=module_order,
                    title=module_title,
                    content=module_content,
                    lessons=lessons,
                )
            )

    modules.sort(key=lambda m: m.order)

    return Course(
        title=course_title,
        duration=duration,
        content=course_content,
        modules=modules,
        root_images=root_images,
    )


def clean_target(site_dir: Path) -> None:
    """Remove generated content from the Antora site directory."""
    pages_dir = site_dir / "modules" / "ROOT" / "pages"
    images_dir = site_dir / "modules" / "ROOT" / "images"

    if pages_dir.exists():
        shutil.rmtree(pages_dir)
    pages_dir.mkdir(parents=True, exist_ok=True)

    if images_dir.exists():
        shutil.rmtree(images_dir)
    images_dir.mkdir(parents=True, exist_ok=True)


def lesson_page_name(module_order: int, lesson: Lesson) -> str:
    """Generate the output page filename for a lesson."""
    return f"{module_order}-{lesson.slug}.adoc"


def module_page_name(module: Module) -> str:
    """Generate the output page filename for a module."""
    return f"{module.slug}.adoc"


def generate_nav(course: Course) -> str:
    """Build nav.adoc content."""
    lines = [f"* xref:index.adoc[{course.title}]"]

    for module in course.modules:
        lines.append(f"* xref:{module_page_name(module)}[{module.title}]")
        for lesson in module.lessons:
            page = lesson_page_name(module.order, lesson)
            lines.append(f"** xref:{page}[{lesson.title}]")

    return "\n".join(lines) + "\n"


def copy_images(course: Course, images_dir: Path) -> int:
    """Copy all images to the Antora images directory. Returns count."""
    count = 0

    # Course root images
    for img in course.root_images:
        shutil.copy2(img, images_dir / img.name)
        count += 1

    # Lesson images
    for module in course.modules:
        for lesson in module.lessons:
            for img in lesson.images:
                if img.is_file():
                    shutil.copy2(img, images_dir / img.name)
                    count += 1

    return count


def main() -> None:
    """Sync course content into Antora site structure."""
    course_dir = load_env()
    site_dir = Path(__file__).parent / "site"

    print(f"Source: {course_dir}")
    print(f"Target: {site_dir}")

    # Discover course structure
    print("Discovering course structure...")
    course = discover_course(course_dir)
    print(f"  Found {len(course.modules)} modules")
    total_lessons = sum(len(m.lessons) for m in course.modules)
    total_questions = sum(
        len(l.questions) for m in course.modules for l in m.lessons
    )
    print(f"  Found {total_lessons} lessons, {total_questions} questions")

    # Clean target
    print("Cleaning target directories...")
    clean_target(site_dir)

    pages_dir = site_dir / "modules" / "ROOT" / "pages"
    images_dir = site_dir / "modules" / "ROOT" / "images"

    # Generate index.adoc from course.adoc
    print("Generating index.adoc...")
    index_content = transform_course(course.content, course.duration)
    (pages_dir / "index.adoc").write_text(index_content)

    # Generate module and lesson pages
    for module in course.modules:
        print(f"  Module {module.order}: {module.title}")

        # Module overview page
        module_content = transform_module(
            module.content, module.order, module.lessons, course.duration
        )
        (pages_dir / module_page_name(module)).write_text(module_content)

        # Lesson pages
        for lesson in module.lessons:
            print(f"    Lesson: {lesson.title}")
            lesson_content = transform_lesson(
                lesson.content, lesson.source_dir, course.duration
            )
            page_name = lesson_page_name(module.order, lesson)
            (pages_dir / page_name).write_text(lesson_content)

    # Generate nav.adoc
    print("Generating nav.adoc...")
    nav_content = generate_nav(course)
    (site_dir / "nav.adoc").write_text(nav_content)

    # Copy images
    img_count = copy_images(course, images_dir)
    if img_count:
        print(f"Copied {img_count} images")

    print(
        f"\nDone! Synced {len(course.modules)} modules, "
        f"{total_lessons} lessons, {total_questions} questions."
    )
    print(f"\nTo build: cd {site_dir} && npm run build")
    print(f"To preview: cd {site_dir} && npm run serve")


if __name__ == "__main__":
    main()
