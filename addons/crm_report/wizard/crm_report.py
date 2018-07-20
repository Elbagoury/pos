from odoo import api, fields, models


class CrmReport(models.TransientModel):
    _name = 'crm.won.lost.report'

    #sales_person = fields.Many2many('res.users', 'ref1', 'ref2', 'user_ref_ids', string="Sales Persons")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    stage_id = fields.Many2one('crm.stage','Stage')
    total = fields.Float("Total Revenue")
    crm_line_ids = fields.One2many('crm.report.line','crm_report_id','CRM Report')
    
    @api.onchange('start_date','end_date','stage_id')
    def onchange_date(self):
		if self.start_date and self.end_date and self.stage_id:
			crm_stages = self.env['crm.lead'].search([('create_date', '>=', self.start_date),('create_date', '<=', self.end_date),('stage_id','=',self.stage_id.id)])
			lead_list = []
			total = 0
			for lead in crm_stages:
				total += lead.planned_revenue
				lead_list.append((0, 0, {'sales_person_id':lead.partner_id.id,'lead_id':lead.id,'revenue':lead.planned_revenue}))
			self.crm_line_ids = lead_list
			self.total = total
			
class crm_report_line(models.TransientModel):
	_name = 'crm.report.line'
	
	sales_person_id = fields.Many2one('res.partner','Sales Person')
	lead_id = fields.Many2one('crm.lead','Lead Name')
	revenue = fields.Float('Expected Revenue')
	
	crm_report_id = fields.Many2one('crm.won.lost.report','CRM Report')
