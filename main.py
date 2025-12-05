import flet as ft
import datetime

# --- لوحة الألوان الاحترافية (تم إصلاح وتوحيد الأسماء) ---
COLORS = {
    "primary": "#2563eb",       
    "primary_dark": "#1d4ed8",  
    "success": "#10b981",       
    "bg_main": "#f8fafc",       
    "white": "#ffffff",
    
    # تصحيح أسماء الألوان لتتوافق مع الكود ومنع الأخطاء
    "text_dark": "#1e293b",     
    "text_main": "#1e293b",     
    "text_light": "#64748b",    
    "text_gray": "#64748b",     
    
    "border": "#e2e8f0",
    "gray_border": "#e2e8f0",   
    "gray_light": "#f8fafc",    
    
    "danger": "#ef4444",        
    "warning": "#f59e0b",       
    
    "blue_50": "#eff6ff",
    "red_50": "#fef2f2",
    "yellow_50": "#fefce8",
    "green_50": "#f0fdf4",
    "purple_50": "#faf5ff",
    "purple_text": "#7e22ce"
}

# --- تنسيقات الأولويات ---
PRIORITY_STYLES = {
    "High": {"bg": COLORS["red_50"], "text": "#b91c1c", "border": "#ef4444", "icon": "🔴", "label": "عالية"},
    "Medium": {"bg": COLORS["yellow_50"], "text": "#a16207", "border": "#eab308", "icon": "🟡", "label": "متوسطة"},
    "Low": {"bg": COLORS["green_50"], "text": "#15803d", "border": "#10b981", "icon": "🟢", "label": "منخفضة"}
}

# --- ثوابت الأيام ---
DAYS_ORDER = ['Unassigned', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
DAYS_AR = {
    'Unassigned': 'غير مجدولة',
    'Saturday': 'السبت', 'Sunday': 'الأحد', 'Monday': 'الاثنين',
    'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء', 'Thursday': 'الخميس', 'Friday': 'الجمعة'
}

# --- القائمة فارغة لتبدأ من الصفر ---
INITIAL_TASKS = []

def main(page: ft.Page):
    # --- إعدادات الصفحة الأساسية ---
    page.title = "Weekly Planner Pro"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = COLORS["bg_main"]
    page.fonts = {"Noto": "https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;700&display=swap"}
    page.theme = ft.Theme(font_family="Noto", color_scheme_seed=COLORS["primary"])
    
    # تعيين أيقونة النافذة (اختياري إذا كان الملف موجوداً)
    # page.window.icon = "assets/icon.png" 

    # متغيرات الحالة
    tasks = list(INITIAL_TASKS)
    current_tab = "today_dashboard"
    editing_task_id = None
    
    today_name_en = datetime.datetime.now().strftime("%A")
    current_date_str = datetime.datetime.now().strftime("%d %B %Y")

    # -------------------------------------------------------------------------
    #  UI HELPERS & FOOTER
    # -------------------------------------------------------------------------
    def get_footer():
        return ft.Container(
            content=ft.Column([
                ft.Divider(height=1, color=COLORS["border"]),
                ft.Row([
                    ft.Text("Developed by Ahmed Azouz", color=COLORS["text_light"], size=11, weight="bold", font_family="Noto"),
                    ft.Icon(ft.Icons.CODE, size=14, color=COLORS["text_light"])
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5)
            ], spacing=15),
            alignment=ft.alignment.center,
            padding=ft.padding.only(top=20, bottom=20, left=20, right=20)
        )

    # -------------------------------------------------------------------------
    #  TIME PICKER LOGIC
    # -------------------------------------------------------------------------
    def handle_time_change(e, text_field):
        if e.control.value:
            time_str = e.control.value.strftime("%H:%M")
            text_field.value = time_str
            text_field.update()

    time_picker_from = ft.TimePicker(
        confirm_text="تأكيد", cancel_text="إلغاء", help_text="بداية المهمة",
        error_invalid_text="وقت غير صحيح", hour_label_text="ساعة", minute_label_text="دقيقة",
    )
    time_picker_to = ft.TimePicker(
        confirm_text="تأكيد", cancel_text="إلغاء", help_text="نهاية المهمة",
        error_invalid_text="وقت غير صحيح", hour_label_text="ساعة", minute_label_text="دقيقة",
    )

    # -------------------------------------------------------------------------
    #  CONTROLS DEFINITION (تعريف الأدوات)
    # -------------------------------------------------------------------------
    def create_field_style(label, multiline=False, read_only=False, icon=None, on_click=None):
        return ft.TextField(
            label=label,
            border_radius=12,
            bgcolor=COLORS["white"],
            border_color=COLORS["border"],
            text_size=14,
            multiline=multiline,
            min_lines=3 if multiline else 1,
            read_only=read_only,
            suffix_icon=icon,
            on_click=on_click,
            focused_border_color=COLORS["primary"],
            focused_border_width=2
        )

    title_tf = create_field_style("عنوان المهمة")
    desc_tf = create_field_style("التفاصيل / ملاحظات", multiline=True)
    
    priority_dd = ft.Dropdown(
        label="الأهمية",
        options=[ft.dropdown.Option(k, f"{v['icon']} {v['label']}") for k, v in PRIORITY_STYLES.items()],
        border_radius=12, bgcolor=COLORS["white"], border_color=COLORS["border"], value="Medium"
    )
    
    category_tf = create_field_style("التصنيف (عمل، دراسة...)")
    
    day_dd = ft.Dropdown(
        label="الموعد",
        options=[ft.dropdown.Option(d, f"{DAYS_AR[d]} {'(اليوم)' if d == today_name_en else ''}") for d in DAYS_ORDER],
        border_radius=12, bgcolor=COLORS["white"], border_color=COLORS["border"], value="Unassigned"
    )
    
    # حقول الوقت
    time_from_tf = create_field_style("من", read_only=True, icon=ft.Icons.ACCESS_TIME, on_click=lambda e: page.open(time_picker_from))
    time_to_tf = create_field_style("إلى", read_only=True, icon=ft.Icons.ACCESS_TIME, on_click=lambda e: page.open(time_picker_to))
    
    time_picker_from.on_change = lambda e: handle_time_change(e, time_from_tf)
    time_picker_to.on_change = lambda e: handle_time_change(e, time_to_tf)

    repeat_cb = ft.Checkbox(label="تكرار هذه المهمة أسبوعياً", value=False, fill_color=COLORS["primary"])
    
    # حاوية الوقت
    time_container = ft.Container(
        content=ft.Row([
            ft.Column([time_from_tf], expand=True), 
            ft.Column([time_to_tf], expand=True)
        ], spacing=10),
        bgcolor=COLORS["blue_50"], padding=15, border_radius=12, visible=False,
        border=ft.border.all(1, COLORS["border"])
    )

    # نوافذ الحوار
    dialog = ft.AlertDialog(
        title_padding=ft.padding.all(20),
        content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
        content=ft.Column([
            title_tf, 
            desc_tf, 
            ft.Row([ft.Column([priority_dd], expand=True), ft.Column([category_tf], expand=True)], spacing=10),
            day_dd, 
            time_container, 
            ft.Container(content=repeat_cb, padding=ft.padding.only(top=10))
        ], height=450, scroll=ft.ScrollMode.HIDDEN, spacing=15)
    )
    confirm_dialog = ft.AlertDialog()

    # -------------------------------------------------------------------------
    #  APP LOGIC
    # -------------------------------------------------------------------------

    def update_view():
        content_area.controls.clear()
        if current_tab == "today_dashboard":
            render_dashboard()
        elif current_tab == "schedule":
            render_schedule()
        elif current_tab == "unassigned":
            render_unassigned()
        update_nav_bar()
        page.update()

    def toggle_task_status(e):
        task_id = e.control.data
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = "done" if t["status"] == "pending" else "pending"
                break
        update_view()

    def on_day_change(e):
        is_visible = day_dd.value != "Unassigned"
        time_container.visible = is_visible
        if e is not None:
            time_container.update()

    day_dd.on_change = on_day_change

    def open_modal(e, task_id=None):
        nonlocal editing_task_id
        editing_task_id = task_id
        
        # Reset or Fill
        if task_id:
            t = next((x for x in tasks if x["id"] == task_id), None)
            title_tf.value = t["title"]
            desc_tf.value = t.get("description", "")
            priority_dd.value = t["priority"]
            category_tf.value = t.get("category", "General")
            day_dd.value = t["day"]
            time_from_tf.value = t.get("timeFrom", "")
            time_to_tf.value = t.get("timeTo", "")
            repeat_cb.value = True if t.get("type") in ["repeated", "fixed"] else False
            dialog.title = ft.Text("تعديل المهمة", weight="bold", size=20)
        else:
            title_tf.value = ""
            desc_tf.value = ""
            priority_dd.value = "Medium"
            category_tf.value = "عام"
            day_dd.value = "Unassigned"
            time_from_tf.value = ""
            time_to_tf.value = ""
            repeat_cb.value = False
            dialog.title = ft.Text("مهمة جديدة", weight="bold", size=20)
        
        # Reset Errors
        title_tf.error_text = None

        dialog.actions = [
            ft.ElevatedButton("حفظ", on_click=save_task, bgcolor=COLORS["primary"], color="white", 
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=15, elevation=0)),
            ft.TextButton("إلغاء", on_click=lambda e: page.close(dialog), style=ft.ButtonStyle(color=COLORS["text_light"]))
        ]
        
        on_day_change(None) 
        page.open(dialog)

    def save_task(e):
        if not title_tf.value:
            title_tf.error_text = "يرجى كتابة عنوان للمهمة"
            dialog.update()
            return
            
        new_data = {
            "title": title_tf.value,
            "description": desc_tf.value,
            "priority": priority_dd.value,
            "category": category_tf.value,
            "day": day_dd.value,
            "timeFrom": time_from_tf.value,
            "timeTo": time_to_tf.value,
            "type": "repeated" if repeat_cb.value else "one-time",
            "status": "pending" 
        }

        if editing_task_id:
            for t in tasks:
                if t["id"] == editing_task_id:
                    new_data["id"] = t["id"]
                    new_data["status"] = t["status"]
                    t.update(new_data)
                    break
        else:
            new_data["id"] = int(datetime.datetime.now().timestamp() * 1000)
            tasks.append(new_data)
        
        page.close(dialog)
        update_view()

    def delete_task_req(e):
        task_id = e.control.data
        def confirm(e):
            nonlocal tasks
            tasks = [t for t in tasks if t["id"] != task_id]
            page.close(confirm_dialog)
            update_view()
            
        confirm_dialog.title = ft.Text("حذف المهمة", weight="bold")
        confirm_dialog.content = ft.Text("هل أنت متأكد من حذف هذه المهمة نهائياً؟")
        confirm_dialog.actions = [
            ft.TextButton("حذف", on_click=confirm, style=ft.ButtonStyle(color=COLORS["danger"])),
            ft.TextButton("إلغاء", on_click=lambda e: page.close(confirm_dialog))
        ]
        page.open(confirm_dialog)

    def reset_week_req(e):
        def execute_reset(e):
            nonlocal tasks
            reset_date = datetime.datetime.now().strftime("%Y-%m-%d")
            updated_tasks = []
            
            for t in tasks:
                is_repeated = t.get("type") in ["repeated", "fixed"]
                
                if t["status"] == "done":
                    if is_repeated:
                        t["status"] = "pending"
                        updated_tasks.append(t)
                    else:
                        continue
                elif t["status"] == "pending":
                    if t["day"] != "Unassigned":
                        if is_repeated:
                            updated_tasks.append(t)
                        else:
                            original_day = DAYS_AR.get(t["day"], t["day"])
                            note = f"\n[أرشيف: {original_day} - {reset_date}]"
                            t["day"] = "Unassigned"
                            t["timeFrom"] = ""
                            t["timeTo"] = ""
                            desc = t.get("description", "")
                            t["description"] = desc + note if desc else note
                            updated_tasks.append(t)
                    else:
                        updated_tasks.append(t)
            
            tasks = updated_tasks
            page.close(confirm_dialog)
            
            snack = ft.SnackBar(ft.Text("تم تصفير الأسبوع وتحديث المهام!", color="white"), bgcolor=COLORS["success"])
            page.overlay.append(snack)
            snack.open = True
            update_view()

        confirm_dialog.title = ft.Text("تصفير الأسبوع", color=COLORS["warning"], weight="bold")
        confirm_dialog.content = ft.Text("سيتم أرشفة المهام غير المنجزة وحذف المنجزة (غير المتكررة).")
        confirm_dialog.actions = [
            ft.TextButton("تأكيد التصفير", on_click=execute_reset, style=ft.ButtonStyle(color=COLORS["warning"])),
            ft.TextButton("إلغاء", on_click=lambda e: page.close(confirm_dialog))
        ]
        page.open(confirm_dialog)

    # -------------------------------------------------------------------------
    #  UI COMPONENTS (بطاقات المهام)
    # -------------------------------------------------------------------------
    def create_task_card(task):
        is_done = task["status"] == "done"
        style = PRIORITY_STYLES.get(task["priority"], PRIORITY_STYLES["Medium"])
        
        tags = [
            ft.Container(
                content=ft.Row([ft.Text(style["icon"], size=10), ft.Text(style["label"], size=10, color=style["text"], weight="bold")], spacing=2),
                bgcolor=style["bg"], padding=ft.padding.symmetric(horizontal=8, vertical=3), border_radius=6
            ),
            ft.Container(
                content=ft.Text(task.get("category", "General"), size=10, color=COLORS["primary"], weight="bold"),
                bgcolor=COLORS["blue_50"], padding=ft.padding.symmetric(horizontal=8, vertical=3), border_radius=6,
            )
        ]
        
        if task["day"] != "Unassigned":
            time_text = f"{task.get('timeFrom')} - {task.get('timeTo')}" if task.get('timeFrom') else "طوال اليوم"
            tags.append(
                ft.Container(
                    content=ft.Row([ft.Icon(ft.Icons.ACCESS_TIME, size=12, color=COLORS["text_light"]), ft.Text(time_text, size=10, color=COLORS["text_light"])], spacing=3),
                    bgcolor=COLORS["gray_light"], padding=ft.padding.symmetric(horizontal=8, vertical=3), border_radius=6
                )
            )
            
        if task.get("type") in ["repeated", "fixed"]:
            tags.append(
                ft.Container(
                    content=ft.Row([ft.Icon(ft.Icons.REPLAY, size=12, color=COLORS["purple_text"]), ft.Text("متكررة", size=10, color=COLORS["purple_text"], weight="bold")], spacing=3),
                    bgcolor=COLORS["purple_50"], padding=ft.padding.symmetric(horizontal=8, vertical=3), border_radius=6
                )
            )

        title_control = ft.Text(
            spans=[
                ft.TextSpan(
                    text=task["title"],
                    style=ft.TextStyle(
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color=COLORS["text_light"] if is_done else COLORS["text_dark"],
                        decoration=ft.TextDecoration.LINE_THROUGH if is_done else ft.TextDecoration.NONE
                    )
                )
            ]
        )

        return ft.Container(
            padding=15, margin=ft.margin.only(bottom=10),
            bgcolor=COLORS["white"],
            border_radius=12,
            border=ft.border.only(right=ft.BorderSide(4, style["border"])),
            shadow=ft.BoxShadow(blur_radius=10, color="#08000000", offset=ft.Offset(0, 4)),
            opacity=0.6 if is_done else 1.0,
            animate_opacity=300,
            content=ft.Row([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.CHECK_CIRCLE_ROUNDED if is_done else ft.Icons.CIRCLE_OUTLINED,
                        icon_color=COLORS["success"] if is_done else COLORS["border"],
                        icon_size=26,
                        on_click=toggle_task_status, data=task["id"]
                    ),
                    ft.Column([
                        title_control,
                        ft.Text(task.get("description", ""), size=12, color=COLORS["text_light"], visible=bool(task.get("description")), no_wrap=False, max_lines=2),
                        ft.Row(tags, wrap=True, spacing=5, run_spacing=5)
                    ], spacing=5, expand=True)
                ], alignment=ft.MainAxisAlignment.START, expand=True),
                
                ft.Column([
                    ft.IconButton(ft.Icons.EDIT_ROUNDED, icon_size=18, icon_color=COLORS["text_light"], on_click=lambda e: open_modal(e, task["id"]), tooltip="تعديل"),
                    ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_size=18, icon_color=COLORS["danger"], on_click=delete_task_req, data=task["id"], tooltip="حذف"),
                ], spacing=0)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START)
        )

    # -------------------------------------------------------------------------
    #  VIEWS (الصفحات)
    # -------------------------------------------------------------------------

    def render_dashboard():
        today_tasks = [t for t in tasks if t["day"] == today_name_en]
        done_cnt = len([t for t in today_tasks if t["status"] == "done"])
        total_cnt = len(today_tasks)
        pending_cnt = total_cnt - done_cnt
        percent = int((done_cnt / total_cnt) * 100) if total_cnt > 0 else 0

        # Stats Cards UI
        def stat_card(label, count, color, bg_color):
            return ft.Container(
                content=ft.Column([
                    ft.Text(str(count), size=24, weight="bold", color=color), 
                    ft.Text(label, size=11, color=COLORS["text_light"])
                ], horizontal_alignment="center", spacing=2),
                bgcolor=COLORS["white"], border_radius=16, padding=15, expand=True,
                shadow=ft.BoxShadow(blur_radius=8, color="#05000000", offset=ft.Offset(0, 4)),
                border=ft.border.all(1, bg_color)
            )

        stats_row = ft.Row([
            stat_card("الكل", total_cnt, COLORS["text_dark"], COLORS["border"]),
            stat_card("منجز", done_cnt, COLORS["success"], COLORS["green_50"]),
            stat_card("متبقي", pending_cnt, COLORS["danger"], COLORS["red_50"]),
        ], spacing=10)

        chart_section = ft.Container()
        if total_cnt > 0:
            chart_section = ft.Container(
                bgcolor=COLORS["white"], padding=20, border_radius=20, margin=ft.margin.only(top=15, bottom=15),
                shadow=ft.BoxShadow(blur_radius=15, color="#08000000"),
                content=ft.Row([
                    ft.Column([
                        ft.Text("إنجاز اليوم", weight="bold", color=COLORS["text_dark"], size=16),
                        ft.Text("ملخص تقدمك الحالي", size=12, color=COLORS["text_light"])
                    ]),
                    ft.Stack([
                        ft.PieChart(
                            sections=[
                                ft.PieChartSection(done_cnt, color=COLORS["success"], radius=18),
                                ft.PieChartSection(pending_cnt, color=COLORS["border"], radius=18),
                            ],
                            center_space_radius=30, height=90, width=90,
                        ),
                        ft.Text(f"{percent}%", size=12, weight="bold", color=COLORS["text_dark"])
                    ], alignment=ft.alignment.center)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        else:
            # هنا التغيير المطلوب لتصميم الحالة الفارغة
            chart_section = ft.Container(
                padding=60, alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Text("🎉", size=50), # رمز الاحتفال
                    ft.Text("رائع! يومك فارغ.", size=16, color=COLORS["text_light"], weight="bold")
                ], horizontal_alignment="center")
            )

        priority_cols = []
        for prio in ["High", "Medium", "Low"]:
            p_tasks = [t for t in today_tasks if t["priority"] == prio]
            if p_tasks:
                priority_cols.append(
                    ft.Container(
                        bgcolor=PRIORITY_STYLES[prio]["bg"], border=ft.border.all(1, PRIORITY_STYLES[prio]["border"]),
                        border_radius=16, padding=15, margin=ft.margin.only(bottom=15),
                        content=ft.Column([
                            ft.Row([
                                ft.Row([ft.Text(PRIORITY_STYLES[prio]['icon']), ft.Text(f"أولوية {PRIORITY_STYLES[prio]['label']}", weight="bold", color=PRIORITY_STYLES[prio]["text"])]),
                                ft.Container(content=ft.Text(str(len(p_tasks)), size=10, weight="bold", color=PRIORITY_STYLES[prio]["text"]), bgcolor="white", padding=ft.padding.symmetric(horizontal=8, vertical=2), border_radius=8)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Column([create_task_card(t) for t in p_tasks], spacing=0)
                        ], spacing=10)
                    )
                )

        content_area.controls.extend([stats_row, chart_section] + priority_cols)
        content_area.controls.append(get_footer())

    def render_schedule():
        header = ft.Row([
            ft.Text("المهام المجدولة", size=20, weight="bold", color=COLORS["text_dark"]),
            ft.OutlinedButton("تصفير الأسبوع", icon=ft.Icons.REPLAY_ROUNDED, 
                              style=ft.ButtonStyle(color=COLORS["danger"], side={"": ft.BorderSide(1, COLORS["danger"])}),
                              on_click=reset_week_req)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        content_area.controls.append(header)
        
        for day in DAYS_ORDER[1:]:
            d_tasks = [t for t in tasks if t["day"] == day]
            is_today = day == today_name_en
            day_color = COLORS["primary"] if is_today else COLORS["text_dark"]
            
            day_content = ft.Column([create_task_card(t) for t in d_tasks]) if d_tasks else ft.Container(
                content=ft.Text("لا يوجد مهام", size=12, color=COLORS["text_light"]), 
                padding=10, border_radius=10, bgcolor=COLORS["white"], 
                alignment=ft.alignment.center, border=ft.border.all(1, COLORS["border"])
            )

            content_area.controls.append(
                ft.Container(
                    border=ft.border.only(left=ft.BorderSide(3, COLORS["primary"] if is_today else COLORS["border"])),
                    padding=ft.padding.only(left=15, bottom=25),
                    margin=ft.margin.only(left=10),
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, size=16, color=day_color),
                            ft.Text(DAYS_AR[day], weight="bold", size=16, color=day_color),
                            ft.Container(content=ft.Text("اليوم", size=10, color="white"), bgcolor=COLORS["primary"], border_radius=20, padding=ft.padding.symmetric(horizontal=8, vertical=2), visible=is_today)
                        ], spacing=8),
                        day_content
                    ], spacing=10)
                )
            )
        content_area.controls.append(get_footer())

    def render_unassigned():
        header = ft.Column([
            ft.Text("المهام المعلقة", size=20, weight="bold", color=COLORS["text_dark"]),
            ft.Text("قائمة المهام التي لم يتم تحديد موعد لها بعد.", size=13, color=COLORS["text_light"]),
        ], spacing=5)
        
        u_tasks = [t for t in tasks if t["day"] == "Unassigned"]
        
        content_area.controls.append(header)
        content_area.controls.append(ft.Divider(height=20, color="transparent"))
        
        if u_tasks:
            content_area.controls.extend([create_task_card(t) for t in u_tasks])
        else:
            content_area.controls.append(
                ft.Container(
                    padding=60, alignment=ft.alignment.center,
                    content=ft.Column([
                        ft.Text("🎉", size=50),
                        ft.Text("رائع! جميع مهامك مجدولة.", size=16, color=COLORS["text_light"], weight="bold")
                    ], horizontal_alignment="center")
                )
            )
        content_area.controls.append(get_footer())

    # -------------------------------------------------------------------------
    #  MAIN LAYOUT ASSEMBLY
    # -------------------------------------------------------------------------
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.HIDDEN)
    
    # App Bar (Header)
    app_bar = ft.Container(
        bgcolor=COLORS["white"], padding=ft.padding.symmetric(horizontal=20, vertical=15),
        shadow=ft.BoxShadow(blur_radius=10, color="#0D000000", offset=ft.Offset(0, 4)),
        content=ft.Row([
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.EVENT_NOTE_ROUNDED, color=COLORS["primary"], size=28), # أيقونة معبرة عن الأجندة
                    ft.Text("اللوحة الرئيسية", weight="bold", size=20, color=COLORS["text_dark"])
                ], spacing=10),
                ft.Row([
                    ft.Icon(ft.Icons.DATE_RANGE_ROUNDED, size=14, color=COLORS["text_light"]),
                    ft.Text(current_date_str, size=12, color=COLORS["text_light"], weight="bold")
                ], spacing=5)
            ], spacing=2),
            
            # زر الإضافة العائم (FAB) بتصميم مربع بحواف دائرية (Squircle)
            ft.FloatingActionButton(
                icon=ft.Icons.POST_ADD, # أيقونة معبرة عن إضافة خطة
                bgcolor=COLORS["primary"], 
                on_click=open_modal, 
                shape=ft.RoundedRectangleBorder(radius=15), # حواف ناعمة
                tooltip="إضافة مهمة جديدة"
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    )

    # Bottom Navigation
    def set_tab(name):
        nonlocal current_tab
        current_tab = name
        update_view()

    def nav_item(icon, label, name):
        is_active = current_tab == name
        color = COLORS["primary"] if is_active else COLORS["text_light"]
        bg = COLORS["blue_50"] if is_active else "transparent"
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=24),
                ft.Text(label, size=11, color=color, weight="bold" if is_active else "normal")
            ], horizontal_alignment="center", spacing=2, alignment=ft.MainAxisAlignment.CENTER),
            padding=10, border_radius=12, bgcolor=bg,
            on_click=lambda e: set_tab(name),
            animate=ft.Animation(200, "easeOut"),
            ink=True
        )

    bottom_nav_content = ft.Container() 

    def update_nav_bar():
        bottom_nav_content.content = ft.Row([
            nav_item(ft.Icons.DASHBOARD_ROUNDED, "الرئيسية", "today_dashboard"),
            nav_item(ft.Icons.CALENDAR_MONTH_ROUNDED, "المجدولة", "schedule"),
            nav_item(ft.Icons.LIST_ALT_ROUNDED, "المعلقة", "unassigned"),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        bottom_nav_content.update()

    bottom_nav = ft.Container(
        bgcolor=COLORS["white"], padding=10,
        border=ft.border.only(top=ft.BorderSide(1, COLORS["border"])),
        shadow=ft.BoxShadow(blur_radius=20, color="#1A000000", offset=ft.Offset(0, -5)),
        content=bottom_nav_content
    )

    layout = ft.Column([
        app_bar,
        ft.Container(content=content_area, expand=True, padding=ft.padding.symmetric(horizontal=20, vertical=10)),
        bottom_nav
    ], expand=True, spacing=0)

    page.add(layout)
    # ft.app(target=main, assets_dir="assets") 
    update_view()

ft.app(target=main, assets_dir="assets")