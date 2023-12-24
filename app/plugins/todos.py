from app.plug import *

class TodoTask(ft.UserControl):
    def __init__(self, id, task_name, completed, task_delete, task_update):
        super().__init__()
        self.id = id
        self.completed = completed
        self.task_name = task_name
        self.task_delete = task_delete
        self.task_update = task_update

    def build(self):
        self.display_task = ft.Checkbox(
            value=self.completed, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1, border=ft.InputBorder.UNDERLINE)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="编辑",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="删除",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="保存",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return ft.Column(controls=[self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.task_update(self.id, self.display_task.label, self.completed)
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_update(self.id, self.display_task.label, self.completed)

    def delete_clicked(self, e):
        self.task_delete(self)


@Plug.register("代办事项")
class TodoApp(UIPlugin):
    """
    管理你的代办事项
    """
    ICON = ft.icons.DONE_OUTLINE
    def process(self, data, search_feild, container, db: dataset.Database, **kwargs):
        self.db = db
        self.table = db.get_table("todos")
        self.new_task = search_feild
        self.new_task.on_submit = self.add_clicked
        self.new_task.on_change = None
        self.container = container
        return self.build()

    def build(self):
        self.tasks = ft.Column(self.load_task())

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="所有"), ft.Tab(text="代办"), ft.Tab(text="已完成")],
        )

        self.items_left = ft.Text("0 items left")

        # application's root control (i.e. "view") containing all other controls
        return ft.Column(
            controls=[
                ft.Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        ft.ListView([
                            self.tasks,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    self.items_left,
                                    ft.OutlinedButton(
                                        text="清空已完成", on_click=self.clear_clicked
                                    ),
                                ],
                            ),
                        ], expand=1)
                    ],
                expand=1),
            ],
        expand=1)
    
    def load_task(self):
        tasks = []
        for row in self.table.all():
            task = TodoTask(row['id'], row['task_name'], row['completed'], self.task_delete, self.task_update)
            tasks.append(task)
        return tasks

    def add_clicked(self, e):
        if self.new_task.value:
            id = self.table.insert(dict(task_name=self.new_task.value, completed=False))
            task = TodoTask(id, self.new_task.value, False, self.task_delete, self.task_update)
            self.tasks.controls.insert(0, task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update()

    def task_update(self, id, name, completed):
        self.table.update(dict(id=id, task_name=name, completed=completed),['id'])
        self.update()

    def task_delete(self, task):
        self.table.delete(id=task.id)
        self.tasks.controls.remove(task)
        self.update()

    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.task_delete(task)

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "所有"
                or (status == "代办" and task.completed == False)
                or (status == "已完成" and task.completed)
            )
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} active item(s) left"
        self.container.update()

