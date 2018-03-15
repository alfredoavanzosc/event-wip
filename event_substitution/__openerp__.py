# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Event Substitution",
    'version': '8.0.1.3.0',
    'license': "AGPL-3",
    'author': "AvanzOSC",
    'website': "http://www.avanzosc.es",
    'contributors': [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es",
    ],
    "category": "Event Management",
    "depends": [
        'event_registration_hr_contract',
    ],
    "data": [
        'wizard/wiz_event_substitution_view.xml',
        'wizard/wiz_event_append_assistant_view.xml',
        'views/event_event_view.xml',
        'views/event_registration_view.xml',
        'views/event_track_view.xml',
        'views/event_track_presence_view.xml',
    ],
    "installable": True,
}
