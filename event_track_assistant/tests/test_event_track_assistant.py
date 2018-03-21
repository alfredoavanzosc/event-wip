﻿# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# Copyright © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import exceptions, fields
from dateutil.relativedelta import relativedelta
from .common import EventTrackAssistantSetup

datetime2str = fields.Datetime.to_string
str2datetime = fields.Datetime.from_string
date2str = fields.Date.to_string


class TestEventTrackAssistant(EventTrackAssistantSetup):

    def setUp(self):
        super(TestEventTrackAssistant, self).setUp()

    def test_event_track_registration_open_button(self):
        self.assertEquals(len(self.event.mapped('track_ids.presences')), 0)
        self.assertFalse(self.partner.registered_partner)
        registration_vals = {
            'event_id': self.event.id,
            'partner_id': self.partner.id,
        }
        registration = self.registration_model.create(registration_vals)
        registration._onchange_partner()
        self.assertTrue(self.partner.registered_partner)
        dict_add_wiz = registration.with_context().button_registration_open()
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).browse(dict_add_wiz.get('res_id'))
        add_wiz.action_append()
        self.assertNotEquals(len(self.event.mapped('track_ids.presences')), 0)
        presence = self.event.track_ids[0].presences[0]
        wiz_complete_presence = self.wiz_presence_model.create({})
        wiz_complete_presence.with_context(
            active_ids=[presence.id]).buttom_complete_presences()
        self.assertEquals(presence.session_duration, presence.real_duration)
        self.assertEquals(presence.state, 'completed')
        presence.button_pending()
        self.assertEquals(presence.real_duration, 0)
        self.assertEquals(presence.state, 'pending')
        presence.button_absent()
        self.assertEquals(presence.state, 'absent')
        configs = self.config_model.search([])
        configs.write({'show_all_customers_in_presences': True})
        presence = self.event.track_ids[0].presences[0]
        configs.write({'show_all_customers_in_presences': False})
        registration.date_start = str2datetime(self.event.date_begin) -\
            relativedelta(days=1)
        self.assertNotEquals(registration.date_start, self.event.date_begin)
        res = registration._onchange_date_start()
        self.assertTrue(res.get('warning'))
        self.assertEquals(registration.date_start, self.event.date_begin)
        registration.date_end = str2datetime(self.event.date_end) +\
            relativedelta(days=1)
        self.assertNotEquals(registration.date_end, self.event.date_end)
        res = registration._onchange_date_end()
        self.assertTrue(res.get('warning'))
        self.assertEquals(registration.date_end, self.event.date_end)
        registration.write({
            'date_start': str2datetime(self.event.date_begin) +
            relativedelta(days=1),
            'date_end': str2datetime(self.event.date_begin) -
            relativedelta(days=1),
        })
        self.assertNotEquals(registration.date_end, self.event.date_end)
        res = registration._onchange_date_end()
        self.assertTrue(res.get('warning'))
        self.assertEquals(registration.date_end, self.event.date_end)
        self.assertEquals(registration._onchange_date_end(), {},
                          'Any date is changed(2)')
        registration.write({
            'date_start': str2datetime(self.event.date_end) +
            relativedelta(days=1),
            'date_end': str2datetime(self.event.date_end) -
            relativedelta(days=1),
        })
        self.assertNotEquals(registration.date_start, self.event.date_begin)
        res = registration._onchange_date_start()
        self.assertTrue(res.get('warning'))
        self.assertEquals(registration.date_start, self.event.date_begin)
        res = registration._onchange_date_start()
        self.assertEquals(registration._onchange_date_start(), {},
                          'Any date is changed')
        registration_vals = {
            'event_id': self.event.id,
            'partner_id': self.partner.id,
            'date_start': registration.date_start,
            'date_end': registration.date_end,
            'name': self.partner.name}
        registration2 = self.registration_model.create(registration_vals)
        with self.assertRaises(exceptions.Warning):
            registration2.button_registration_open()
        registration2.state = 'done'
        with self.assertRaises(exceptions.Warning):
            registration2.unlink()
        settings_model = self.env['marketing.config.settings']
        settings = settings_model.search([])
        settings.unlink()
        presence.state = 'pending'
        presence._compute_allowed_partner_ids()
        self.assertEquals(presence.allowed_partner_ids,
                          presence.session.allowed_partner_ids)

    def test_event_track_assistant_delete(self):
        settings_model = self.env['marketing.config.settings']
        self.assertEquals(len(self.event.mapped('registration_ids')), 0)
        self.assertEquals(self.partner.session_count, 0)
        self.assertEquals(self.partner.presences_count, 0)
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create(
            {'partner': self.partner.id,
             'from_date': self.event.date_begin,
             'min_from_date': self.event.date_begin,
             'max_to_date': self.event.date_end,
             'to_date': self.event.date_end})
        add_wiz.action_append()
        self.partner.invalidate_cache()
        self.assertNotEquals(len(self.event.mapped('registration_ids')), 0)
        self.assertNotEquals(self.partner.session_count, 0)
        self.assertNotEquals(self.partner.presences_count, 0)
        self.assertIn(
            self.partner.id,
            self.event.mapped('registration_ids.partner_id').ids,
            'Partner should be registered')
        show_sessions = self.partner.show_sessions_from_partner()
        self.assertEquals(
            show_sessions.get('res_model'), 'event.track')
        self.assertEquals(
            self.partner.event_locations_count, 0,
            'BAD partner event locations count')
        show_events = self.partner.show_event_locations_from_partner()
        self.assertEquals(
            show_events.get('res_model'), 'event.event')
        self.assertEquals(
            self.partner.event_organizer_count, 0,
            'BAD partner event organizer count')
        show_events = self.partner.show_event_organizer_from_partner()
        self.assertEquals(
            show_events.get('res_model'), 'event.event')
        self.assertEquals(
            self.partner.registrations_location_organizer_count, 0,
            'BAD partner registrations location organizer count')
        show_registrations = (
            self.partner.show_registrations_location_organizer_from_partner())
        self.assertEquals(
            show_registrations.get('res_model'), 'event.registration')
        show_presences = self.partner.show_presences_from_partner()
        self.assertEquals(
            show_presences.get('res_model'), 'event.track.presence')
        presences = self.event.mapped('track_ids.presences')
        self.assertNotEquals(len(presences), 0)
        new_presence = self.presence_model.create({
            'session': self.event.track_ids[:1].id,
            'partner': self.partner.id,
            'name': self.partner.name
        })
        self.assertEquals(new_presence.event, self.event)
        settings_model._write_or_create_param(
            'show.all.customers.in.presences', False)
        self.assertIn(self.partner, new_presence.allowed_partner_ids)
        registration = self.event.registration_ids[:1]
        dict_del_wiz = registration.new_button_reg_cancel()
        self.assertNotEquals(registration.state, 'cancel')
        del_wiz = self.wiz_del_model.with_context(
            active_ids=self.event.ids).browse(dict_del_wiz.get('res_id'))
        from_date = del_wiz.from_date
        to_date = del_wiz.to_date
        self.assertFalse(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': to_date,
        })
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': '2025-01-25',
        })
        self.assertTrue(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': '2025-01-25',
        })
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': to_date,
        })
        with self.assertRaises(exceptions.Warning):
            del_wiz.action_delete()
        del_wiz.write({
            'notes': 'Registration canceled by test',
        })
        del_wiz.action_delete()
        self.assertEquals(registration.state, 'cancel')

    def test_event_track_assistant_delete_from_event(self):
        self.assertEquals(len(self.event.mapped('registration_ids')), 0)
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create(
            {'partner': self.partner.id,
             'from_date': self.event.date_begin,
             'min_from_date': self.event.date_begin,
             'max_to_date': self.event.date_end,
             'to_date': self.event.date_end})
        add_wiz.action_append()
        self.assertNotEquals(len(self.event.mapped('registration_ids')), 0)
        del_wiz = self.wiz_del_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id})
        self.assertFalse(del_wiz.registration)
        from_date = del_wiz.from_date
        to_date = del_wiz.to_date
        self.assertFalse(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': to_date,
        })
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': '2025-01-25',
        })
        self.assertTrue(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': '2025-01-25',
        })
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': to_date,
        })
        with self.assertRaises(exceptions.Warning):
            del_wiz.action_delete()
        del_wiz.write({
            'notes': 'Registration canceled by test',
        })
        del_wiz.action_delete()
        registration = self.event.registration_ids.filtered(
            lambda r: r.partner_id == self.partner)
        self.assertEquals(registration.state, 'cancel')
        registration._cancel_registration(
            '2025-01-29', '2025-01-30', '2025-01-01', 'notes')
        registration._cancel_registration(
            '2025-01-20', '2025-01-25', '2025-01-01', 'notes')

    def test_event_assistant_track_assistant_confirm_assistant(self):
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create(
            {'partner': self.partner.id,
             'from_date': self.event.date_begin,
             'min_from_date': self.event.date_begin,
             'max_to_date': self.event.date_end,
             'to_date': self.event.date_end})
        add_wiz.action_append()
        registration = self.event.registration_ids[:1]
        wiz_vals = {'name': 'confirm assistants'}
        wiz = self.wiz_confirm_model.create(wiz_vals)
        wiz.with_context(
            active_ids=self.event.ids).action_confirm_assistant()
        self.assertNotEqual(
            registration.state, 'draft',
            'Registration should have been confirmed.')
        wiz_impute = self.wiz_impute_model.with_context(
            active_ids=self.event.track_ids.ids).create({})
        self.assertNotEquals(len(wiz_impute.lines), 0)
        wiz_impute.lines.write({
            'create_claim': True,
        })
        with self.assertRaises(exceptions.Warning):
            wiz_impute.button_impute_hours()
        wiz_impute.lines.write({
            'notes': 'Created claim from event.track.presence',
        })
        self.assertEquals(len(self.event.claim_ids), 0)
        self.assertEquals(self.event.claim_count, 0)
        wiz_impute.button_impute_hours()
        self.assertNotEqual(len(self.event.claim_ids), 0)
        self.assertNotEqual(self.event.claim_count, 0)
        for track in self.event.track_ids:
            self.assertNotEqual(len(track.claim_ids), 0)
            self.assertNotEqual(track.claim_count, 0)

    def test_wiz_event_registration_confirm(self):
        registration_vals = {
            'event_id': self.event.id,
            'partner_id': self.partner.id,
            'date_start': self.event.date_begin,
            'date_end': self.event.date_end
        }
        registration = self.registration_model.create(registration_vals)
        reg_confirm_model = self.env['wiz.event.registration.confirm']
        wiz = reg_confirm_model.create({'name': 'test from assistant'})
        wiz.with_context(
            active_ids=registration.ids).action_confirm_registrations()
        self.assertEquals(registration.state, 'open')
        self.partner.event_registration_warn = 'block'
        self.partner.event_registration_warn_msg = 'Warn message'
        res = registration._onchange_partner()
        warning = res.get('warning')
        self.assertEquals(warning.get('message'), 'Warn message')
        registration.partner_id = self.partner.id
        self.partner.event_registration_warn = 'warning'
        res = registration._onchange_partner()
        warning = res.get('warning')
        self.assertEquals(warning.get('message'), 'Warn message')
        self.assertEquals(registration.date_start, self.event.date_begin)

    def test_marketing_config_settings(self):
        settings_model = self.env['marketing.config.settings']
        settings_model.set_parameters()
        res = settings_model.get_default_parameters()
        self.assertEquals(res.get('show_all_customers_in_presences'),
                          False, 'Bad marketing settings')
