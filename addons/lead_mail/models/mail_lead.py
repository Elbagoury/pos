from odoo import api, fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    mail_subject = fields.Char("Mail Subject")
    lead_mail_ids = fields.One2many('mail.message','crm_lead_id',compute = '_compute_mail')

    @api.one
    def _compute_mail(self):
        message_list = []
        for lead in self:
            for message in self.env['mail.message'].search([('subject', '=', lead.mail_subject)]):
                message_list.append(message.id)
        self.lead_mail_ids = message_list

class Message(models.Model):
    _inherit = "mail.message"
    
    crm_lead_id = fields.Many2one('crm.lead','Lead')