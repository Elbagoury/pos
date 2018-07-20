import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError


class pay_in_out_report(models.TransientModel):
	_name = 'pay.in.out.report'
	
	date = fields.Date('Date')
	pay_in_out_ids = fields.One2many('pay.in.out.line','pay_in_out_id','Pay In/out')
	
	@api.onchange('date')
	def onchange_date(self):
		if self.date:
			account_ids = self.env['account.bank.statement.line'].search([('date','=',self.date),('pos_statement_id','=',False)])
			pay_in_out_list = []
			for account in account_ids:
				if account.amount > 0:
					pay_in_out_list.append((0, 0, {'label':account.name,'pay_in':account.amount}))
				else:
					pay_in_out_list.append((0, 0, {'label':account.name,'pay_out':-(account.amount)}))

			self.pay_in_out_ids = pay_in_out_list
	
class pay_in_out_line(models.TransientModel):
	_name = 'pay.in.out.line'
	
	label = fields.Char('Purpose')
	pay_in = fields.Float('Paid In')
	pay_out = fields.Float('Paid Out')
	pay_in_out_id = fields.Many2one('pay.in.out.report','Pay In/out')
