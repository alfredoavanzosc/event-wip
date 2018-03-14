# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Order Create Event",
    "version": "8.0.2.1.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es",
    ],
    "category": "Event Management",
    "depends": [
        "account",
        "analytic",
        "partner_event",
        "event_sale",
        "event_project",
        "event_track_assistant",
        "calendar_holiday",
        "procurement_service_project",
        "project_task_generated_with_product_performance",
        "hr_employee_catch_partner",
        "web_sheet_full_width",
        "web_context_tunnel",
        "sale_service_recurrence_configurator",
        "resource"
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wiz_event_append_assistant_view.xml",
        "wizard/wiz_change_session_date_view.xml",
        "wizard/wiz_recalculate_hour_from_contract_view.xml",
        "report/event_track_presence_report_view.xml",
        "views/account_analytic_account_view.xml",
        "views/sale_order_view.xml",
        "views/project_project_view.xml",
        "views/project_task_view.xml",
        "views/event_event_view.xml",
        "views/event_track_view.xml",
        "views/product_view.xml",
        "views/resource_calendar_view.xml",
        "views/hr_employee_view.xml",
    ],
    "installable": True,
}
