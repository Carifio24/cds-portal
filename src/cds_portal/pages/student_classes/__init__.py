from datetime import datetime

import solara
from solara.alias import rv
from solara.server import settings

from ...components.join_class import JoinClass
from ...remote import BASE_API


@solara.component
def JoinClassDialog(callback: callable = lambda: None):
    active = solara.use_reactive(False)

    class_code = solara.use_reactive("")
    student_validation_message = solara.use_reactive("")

    def _on_join_clicked(*args):
        class_exists = BASE_API.validate_class_code(class_code.value)

        if not class_exists:
            student_validation_message.set("Class does not exist.")
            return

        student_response = BASE_API.add_student_to_class(
            class_code.value, BASE_API.hashed_user
        )

        if student_response.status_code != 200:
            student_validation_message.set(student_response.reason)
            return

        callback()
        active.set(False)

    with rv.Dialog(
        v_model=active.value,
        on_v_model=active.set,
        v_slots=[
            {
                "name": "activator",
                "variable": "x",
                "children": rv.Btn(
                    v_on="x.on",
                    v_bind="x.attrs",
                    children=["Join Class"],
                    elevation=0,
                ),
            }
        ],
        max_width=600,
    ) as dialog:
        with rv.Card(outlined=True):
            with rv.CardTitle():
                rv.Html(tag="text-h5", children=["Join a New Class"])

            rv.Divider()

            with rv.CardText(class_="mt-8"):
                JoinClass(class_code, student_validation_message)

            rv.Divider()

            with rv.CardActions():
                rv.Spacer()

                solara.Button("Cancel", on_click=lambda: active.set(False), elevation=0)
                solara.Button(
                    "Join",
                    color="success",
                    on_click=_on_join_clicked,
                    elevation=0,
                )

    return dialog


@solara.component
def Page():
    classes = solara.use_reactive([])
    selected_rows, set_selected_rows = solara.use_state([])

    def _retrieve_classes():
        classes_response = BASE_API.load_student_classes()
        formatted_classes = []

        for cls in classes_response:
            educator_response = BASE_API.load_educator_info(cls["educator_id"])

            cls_fmt = {
                "name": cls["name"],
                "code": cls["code"],
                "educator": f"{educator_response['first_name']} {educator_response['last_name']}",
                "date": datetime.fromisoformat(cls["created"]).strftime("%m/%d/%Y"),
            }

            formatted_classes.append(cls_fmt)

        classes.set(formatted_classes)

    solara.use_effect(_retrieve_classes, [])

    with solara.Row(classes=["fill-height"]):
        with rv.Col(cols=12):
            with rv.Row(class_="pa-0 mb-8 mx-0"):
                solara.Text("Class Overview", classes=["display-1"])
                rv.Spacer()
                JoinClassDialog(callback=_retrieve_classes)

            rv.DataTable(
                items=classes.value,
                single_select=False,
                show_select=False,
                v_model=selected_rows,
                on_v_model=set_selected_rows,
                headers=[
                    {"text": "Date", "value": "date", "sortable": True},
                    {
                        "text": "Name",
                        "align": "start",
                        "sortable": True,
                        "value": "name",
                    },
                    {"text": "Educator", "value": "educator"},
                    {"text": "Code", "value": "code"},
                    {"text": "", "value": "actions", "align": "end"},
                ],
                v_slots=[
                    {
                        "name": "item.actions",
                        "variable": "y",
                        "children": [
                            solara.Button(
                                "Launch",
                                text=False,
                                icon_name="mdi-pencil",
                                # outlined=True,
                                depressed=True,
                                color="success",
                                href=f"{settings.main.base_url}hubbles-law",
                                target="_blank",
                            ),
                            # rv.Btn(
                            #     icon=True,
                            #     # on_click=lambda: print("Delete"),
                            #     children=[rv.Icon(children=["mdi-delete"])],
                            # ),
                        ],
                    },
                ],
            )
