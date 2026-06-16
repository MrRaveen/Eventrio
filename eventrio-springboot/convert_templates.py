import re
import shutil
from pathlib import Path

src = Path("templates-source")
dst = Path("eventrio-web-service/src/main/resources/templates")

if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

replacements = [
    (r"\{% extends 'base.html' %\}\s*\n", ""),
    (r"\{% block content %\}\s*\n", ""),
    (r"\{% block scripts %\}\s*\n", ""),
    (r"\{% endblock %\}\s*\n", ""),
    (r"\{% include 'components/confirm_modal.html' %\}", '<div th:replace="~{components/confirm_modal :: modal}"></div>'),
    (r"\{% include 'components/dashboard/sidebar.html' %\}", '<div th:replace="~{components/dashboard/sidebar :: sidebar}"></div>'),
    (r"\{% include 'components/dashboard/tab_tasks.html' %\}", '<div th:replace="~{components/dashboard/tab_tasks :: tasks}"></div>'),
    (r"\{% include 'components/dashboard/tab_calendar.html' %\}", '<div th:replace="~{components/dashboard/tab_calendar :: calendar}"></div>'),
    (r"\{% include 'components/dashboard/tab_media.html' %\}", '<div th:replace="~{components/dashboard/tab_media :: media}"></div>'),
    (r"\{% include 'components/dashboard/tab_script.html' %\}", '<div th:replace="~{components/dashboard/tab_script :: script}"></div>'),
    (r"\{% include 'components/slideshow.html' %\}", '<div th:replace="~{components/slideshow :: slideshow}"></div>'),
    (r"\{% include 'components/dashboard/tab_meeting.html' %\}", '<div th:replace="~{components/dashboard/tab_meeting :: meeting}"></div>'),
    (r"\{% include 'components/dashboard/tab_contributors.html' %\}", '<div th:replace="~{components/dashboard/tab_contributors :: contributors}"></div>'),
    (r"\{% include 'components/dashboard/modals.html' %\}", '<div th:replace="~{components/dashboard/modals :: modals}"></div>'),
    (r"\{\{ url_for\('auth_login.login'\) \}\}", "@{/login}"),
    (r"\{\{ url_for\('auth_login.google_login'\) \}\}", "@{/oauth2/authorization/google}"),
    (r"\{\{ url_for\('auth_login.logout'\) \}\}", "@{/logout}"),
    (r"\{\{ url_for\('auth_login.setup_profile'\) \}\}", "@{/setup-profile}"),
    (r"\{\{ url_for\('ui_endpoints.landing'\) \}\}", "@{/}"),
    (r"\{\{ url_for\('ui_endpoints.pricing'\) \}\}", "@{/pricing}"),
    (r"\{\{ url_for\('ui_endpoints.dashboard'\) \}\}", "@{/dashboard}"),
    (r"\{\{ url_for\('ui_endpoints.ai_planner'\) \}\}", "@{/ai-planner}"),
    (r"\{\{ url_for\('ui_endpoints.browse_events'\) \}\}", "@{/browse-events}"),
    (r"\{\{ url_for\('ui_endpoints.user_profile_ui'\) \}\}", "@{/user-profile-ui}"),
    (r"\{\{ url_for\('ui_endpoints.dashboard', tab='engagement'\) \}\}", "@{/dashboard(tab=engagement)}"),
    (r"\{\{ url_for\('ui_endpoints.dashboard', tab='orgs'\) \}\}", "@{/dashboard(tab=orgs)}"),
    (r"\{\{ url_for\('ui_endpoints.dashboard', tab='collabs'\) \}\}", "@{/dashboard(tab=collabs)}"),
    (r"\{\{ url_for\('ui_endpoints.dashboard', tab='profile'\) \}\}", "@{/dashboard(tab=profile)}"),
    (r"\{\{ url_for\('ui_endpoints.dashboard', tab='social_setup'\) \}\}", "@{/dashboard(tab=social_setup)}"),
    (r"\{\{ url_for\('ui_endpoints.dashboard', tab='settings'\) \}\}", "@{/dashboard(tab=settings)}"),
    (r"\{\{ url_for\('ui_endpoints.browse_events', selected=event.id\|string\) \}\}", "@{/browse-events(selected=${event.id})}"),
    (r"\{\{ url_for\('ui_endpoints.event_dashboard', event_id=event.id, tab='tasks'\) \}\}", "@{/event-dashboard/{id}(id=${event.id},tab=tasks)}"),
    (r"\{\{ url_for\('ui_endpoints.event_dashboard', event_id=event.id, tab='calendar'\) \}\}", "@{/event-dashboard/{id}(id=${event.id},tab=calendar)}"),
    (r"\{\{ url_for\('ui_endpoints.event_dashboard', event_id=event.id, tab='media'\) \}\}", "@{/event-dashboard/{id}(id=${event.id},tab=media)}"),
    (r"\{\{ url_for\('ui_endpoints.event_dashboard', event_id=event.id, tab='script'\) \}\}", "@{/event-dashboard/{id}(id=${event.id},tab=script)}"),
    (r"\{\{ url_for\('ui_endpoints.event_dashboard', event_id=event.id, tab='meeting'\) \}\}", "@{/event-dashboard/{id}(id=${event.id},tab=meeting)}"),
    (r"\{\{ url_for\('ui_endpoints.event_dashboard', event_id=event.id, tab='slideshow'\) \}\}", "@{/event-dashboard/{id}(id=${event.id},tab=slideshow)}"),
    (r"\{\{ url_for\('ui_endpoints.event_dashboard', event_id=event.id, tab='contributors'\) \}\}", "@{/event-dashboard/{id}(id=${event.id},tab=contributors)}"),
    (r"\{\{ url_for\('payment.create_checkout_session'\) \}\}", "@{/payment/create-checkout-session}"),
    (r"\{\{ url_for\('main_dashboard.chat_main'\) \}\}", "@{/dashboard(tab=engagement)}"),
    (r"\{\{ error_code \}\}", "[[${error_code}]]"),
    (r"\{\{ error_title \}\}", "[[${error_title}]]"),
    (r"\{\{ error_message \}\}", "[[${error_message}]]"),
    (r"/event-ui/event-dashboard/\$\{projectID\}", "/event-dashboard/${projectID}"),
]

fragment_names = {
    "components/confirm_modal.html": "modal",
    "components/dashboard/sidebar.html": "sidebar",
    "components/dashboard/tab_tasks.html": "tasks",
    "components/dashboard/tab_calendar.html": "calendar",
    "components/dashboard/tab_media.html": "media",
    "components/dashboard/tab_script.html": "script",
    "components/slideshow.html": "slideshow",
    "components/dashboard/tab_meeting.html": "meeting",
    "components/dashboard/tab_contributors.html": "contributors",
    "components/dashboard/modals.html": "modals",
}


def th_expr(expr: str) -> str:
    """Wrap a Thymeleaf expression for use inside ${...}."""
    return "${" + _jinja_expr_to_thymeleaf(expr) + "}"


def _python_to_java_date_pattern(pattern: str) -> str:
    """Convert Python strftime patterns to Java DateTimeFormatter patterns."""
    replacements = [
        ("%b %d, %Y", "MMM dd, yyyy"),
        ("%B %d, %Y", "MMMM dd, yyyy"),
        ("%b %d", "MMM dd"),
        ("%Y-%m-%d", "yyyy-MM-dd"),
        ("%H:%M", "HH:mm"),
        ("%I:%M %p", "hh:mm a"),
    ]
    for py, java in replacements:
        pattern = pattern.replace(py, java)
    return pattern


def _jinja_expr_to_thymeleaf(expr: str) -> str:
    expr = expr.strip()
    expr = re.sub(r"\bnot\s+", "!", expr)
    expr = re.sub(r"\band\b", " and ", expr)
    expr = re.sub(r"\bor\b", " or ", expr)
    expr = expr.replace(" is not string", " instanceof T(java.lang.String) == false")
    expr = expr.replace(" is string", " instanceof T(java.lang.String)")
    expr = expr.replace(" is mapping", " instanceof T(java.util.Map)")
    expr = re.sub(r"(\w+)\.get\('([^']+)'\)", r"\1['\2']", expr)
    expr = expr.replace("|length", ".size")
    expr = re.sub(r"\buser and user\.(\w+)", r"user != null and user.\1 != null", expr)
    expr = re.sub(r"\buser\b(?!\s*[!=.])", "user != null", expr)
    return expr


def convert_script_conditionals(content: str) -> str:
    """Convert {% if %} inside <script> blocks to inline JS conditionals."""

    def fix_script(m: re.Match) -> str:
        script = m.group(0)
        script = re.sub(
            r"\{%\s*if\s+([^%]+)\s*%\}\s*([\s\S]*?)\s*\{%\s*endif\s*%\}",
            lambda im: "if (" + _js_condition(im.group(1)) + ") {\n" + im.group(2).strip() + "\n}",
            script,
        )
        return script

    def _js_condition(cond: str) -> str:
        cond = cond.strip()
        m = re.match(r"active_tab\s*==\s*'([^']+)'", cond)
        if m:
            tab = m.group(1)
            return f"/*[[${{active_tab}}]]*/ 'profile' === '{tab}'"
        return "true"

    return re.sub(r"<script[^>]*>[\s\S]*?</script>", fix_script, content)


def convert_inline_class_conditionals(content: str) -> str:
    """Convert Jinja conditionals embedded in class attributes to th:classappend."""

    def repl_block(m: re.Match) -> str:
        prefix = m.group(1).rstrip()
        inner = m.group(2)
        th_expr_val = _class_if_chain_to_thymeleaf(inner)
        return f'class="{prefix}" th:classappend="{th_expr_val}"'

    pattern = re.compile(
        r'class="([^"]*?)\s*(\{%\s*if[\s\S]*?\{%\s*endif\s*%\})"',
        re.MULTILINE,
    )
    return pattern.sub(repl_block, content)


def _class_if_chain_to_thymeleaf(inner: str) -> str:
    """Build a nested ternary for if/elif/else class fragments."""
    parts: list[tuple[str, str]] = []
    else_val = ""
    for m in re.finditer(
        r"\{%\s*(if|elif|else)\s*(.*?)\s*%\}([\s\S]*?)(?=\{%\s*(?:elif|else|endif)\s*%\}|$)",
        inner,
    ):
        tag, cond, val = m.group(1), m.group(2).strip(), m.group(3).strip()
        if tag == "else":
            else_val = val
        else:
            parts.append((_jinja_expr_to_thymeleaf(cond), val))

    expr = f"'{else_val}'"
    for cond, val in reversed(parts):
        expr = f"({cond}) ? '{val}' : {expr}"
    return "${" + expr + "}"


def convert_jinja_control_blocks(content: str) -> str:
    """Convert {% if %}/{% elif %}/{% else %}/{% endif %} and for loops."""
    token_re = re.compile(r"\{%\s*(if|elif|else|endif|for|endfor|set)\s*(.*?)\s*%\}", re.DOTALL)

    out: list[str] = []
    last = 0
    stack: list[dict] = []

    for m in token_re.finditer(content):
        out.append(content[last : m.start()])
        tag = m.group(1)
        raw_expr = m.group(2).strip()

        if tag == "if":
            expr = _jinja_expr_to_thymeleaf(raw_expr)
            stack.append({"conditions": [expr]})
            out.append(f'<th:block th:if="${{{expr}}}">')
        elif tag == "elif":
            if not stack:
                last = m.end()
                continue
            frame = stack[-1]
            expr = _jinja_expr_to_thymeleaf(raw_expr)
            prior = " or ".join(f"({c})" for c in frame["conditions"])
            unless = prior if prior else "false"
            frame["conditions"].append(expr)
            out.append(f'</th:block><th:block th:if="${{{expr}}}" th:unless="${{{unless}}}">')
        elif tag == "else":
            if not stack:
                last = m.end()
                continue
            frame = stack[-1]
            prior = " or ".join(f"({c})" for c in frame["conditions"])
            unless = f"({prior})" if prior else "false"
            out.append(f'</th:block><th:block th:unless="${{{unless}}}">')
        elif tag == "endif":
            if stack:
                stack.pop()
            out.append("</th:block>")
        elif tag == "for":
            m_for = re.match(r"(\w+)\s+in\s+(.+)", raw_expr)
            if m_for:
                var, seq = m_for.group(1), m_for.group(2).strip()
                out.append(f'<th:block th:each="{var} : ${{{seq}}}">')
            else:
                out.append("")
        elif tag == "endfor":
            out.append("</th:block>")
        elif tag == "set":
            # {% set s = expr %} -> handled inline where possible; drop standalone set
            out.append("")

        last = m.end()

    out.append(content[last:])
    return "".join(out)


def _inline_expr(inner: str) -> str:
    """Convert a Jinja {{ ... }} expression to Thymeleaf [[${...}]]."""
    inner = inner.strip()
    ternary = re.match(r"(.+?)\s+if\s+(.+?)\s+else\s+(.+)", inner, re.DOTALL)
    if ternary:
        true_val, cond, false_val = ternary.group(1).strip(), ternary.group(2).strip(), ternary.group(3).strip()
        cond = _jinja_expr_to_thymeleaf(cond)
        true_val = _convert_value_expr(true_val)
        false_val = _convert_value_expr(false_val)
        return f"[[${{{cond} ? {true_val} : {false_val}}}]]"
    return _format_inline(_convert_value_expr(inner))


def _format_inline(expr: str) -> str:
    return f"[[${{{expr}}}]]"


def convert_python_ternary_variables(content: str) -> str:
    """Convert Jinja {{ ... }} expressions to Thymeleaf inline."""
    return re.sub(r"\{\{\s*([^}]+?)\s*\}\}", lambda m: _inline_expr(m.group(1)), content)


def _convert_value_expr(expr: str) -> str:
    expr = expr.strip()
    if "|" in expr:
        base, _, filters = expr.partition("|")
        base = _convert_value_expr(base.strip())
        for f in filters.split("|"):
            f = f.strip()
            if f == "urlencode":
                base = f"#uris.encode({base})"
            elif f == "capitalize":
                base = f"#strings.capitalize({base})"
            elif f == "tojson":
                base = f"#strings.escapeJavaScript({base})"
            elif f.startswith("default("):
                default_val = f[8:-1].strip("'\"")
                base = f"({base} ?: '{default_val}')"
            elif f == "escape":
                base = f"#strings.escapeXml({base})"
            elif f.endswith(".lower()"):
                base = f"#strings.toLowerCase({base})"
        return base
    if expr.endswith(" or ''") or " or " in expr:
        parts = re.split(r"\s+or\s+", expr)
        left = _convert_value_expr(parts[0])
        right = _convert_value_expr(parts[1]) if len(parts) > 1 else "''"
        return f"({left} ?: {right})"
    if "~" in expr:
        parts = [p.strip() for p in expr.split("~")]
        return " + ".join(_convert_value_expr(p) for p in parts)
    m = re.match(r"^\((.+)\)$", expr)
    if m:
        return _convert_value_expr(m.group(1))
    m = re.match(r"(\w+(?:\.\w+)+)\[0\]", expr)
    if m:
        return f"#strings.substring({m.group(1)},0,1)"
    m = re.match(r"(\w+(?:\.\w+)+)\[:1\]\.upper\(\)", expr)
    if m:
        base = m.group(1)
        return f"#strings.toUpperCase(#strings.substring({base},0,1))"
    m = re.match(r"(\w+(?:\.\w+)*)\.strftime\('([^']+)'\)", expr)
    if m:
        java_pattern = _python_to_java_date_pattern(m.group(2))
        return f"#temporals.format({m.group(1)}, '{java_pattern}')"
    m = re.match(r"(\w+(?:\.\w+)*)\|truncate\((\d+),\s*true,\s*''\)", expr)
    if m:
        return f"#strings.abbreviate({m.group(1)}, {m.group(2)})"
    if re.match(r"^[\w.]+$", expr):
        return expr
    if expr.startswith("'") or expr.startswith('"'):
        return expr
    return expr


def convert_remaining_variables(content: str) -> str:
    """No-op: all {{ }} handled by convert_python_ternary_variables."""
    return content


for html in dst.rglob("*.html"):
    content = html.read_text(encoding="utf-8")
    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    rel = html.relative_to(dst).as_posix()
    if rel in fragment_names:
        fragment = fragment_names[rel]
        if "th:fragment=" not in content:
            content = (
                f'<div xmlns:th="http://www.thymeleaf.org" th:fragment="{fragment}">\n'
                f"{content.strip()}\n</div>"
            )
    elif html.name == "base.html":
        content = content.replace(
            '<html lang="en" class="light">',
            '<html lang="en" class="light" xmlns:th="http://www.thymeleaf.org" th:fragment="layout(content)">',
        )
        content = re.sub(
            r"<body[^>]*>.*?</body>",
            """<body class="min-h-screen antialiased">
    <th:block th:replace="${content}" />
    <div th:replace="~{components/confirm_modal :: modal}"></div>

    <!-- Theme toggle script -->
    <script>
        function toggleTheme() {
            var html = document.documentElement;
            var next = html.classList.contains('dark') ? 'light' : 'dark';
            html.className = next;
            localStorage.setItem('eventrio-theme', next);
            document.querySelectorAll('.theme-icon-light').forEach(el => el.style.display = next === 'light' ? 'none' : 'block');
            document.querySelectorAll('.theme-icon-dark').forEach(el => el.style.display = next === 'dark' ? 'none' : 'block');
        }
        document.addEventListener('DOMContentLoaded', function() {
            var t = document.documentElement.className;
            document.querySelectorAll('.theme-icon-light').forEach(el => el.style.display = t === 'light' ? 'none' : 'block');
            document.querySelectorAll('.theme-icon-dark').forEach(el => el.style.display = t === 'dark' ? 'none' : 'block');
        });
    </script>
</body>""",
            content,
            flags=re.DOTALL,
        )
    else:
        if 'th:replace="~{base :: layout' not in content:
            content = (
                "<!DOCTYPE html>\n<html xmlns:th=\"http://www.thymeleaf.org\" "
                'th:replace="~{base :: layout(~{::section})}">\n<body>\n'
                f"<section th:fragment=\"section\">\n{content}\n</section>\n</body>\n</html>"
            )

    content = convert_script_conditionals(content)
    content = convert_inline_class_conditionals(content)
    content = convert_jinja_control_blocks(content)
    content = convert_python_ternary_variables(content)
    content = convert_remaining_variables(content)
    content = re.sub(r'href="(@\{[^"]+\})"', r'th:href="\1"', content)
    content = re.sub(r'action="(@\{[^"]+\})"', r'th:action="\1"', content)
    content = re.sub(r"\{%[^%]*%\}", "", content)
    content = re.sub(r"\{\{[^}]*\}\}", "", content)

    html.write_text(content, encoding="utf-8")

print("Converted", len(list(dst.rglob("*.html"))), "templates")
