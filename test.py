import flet as ft

md = """
[Go to Google](https://www.google.com)
"""

def main(page: ft.Page):
    page.add(
        ft.Markdown(
            md,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            auto_follow_links=True,
        )
    )

ft.app(main)