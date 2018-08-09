from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError

class Lead(models.Model):
    _inherit = "crm.lead"

    source = fields.Many2one('source.name','Source')
    pre_experience = fields.Selection([('1','Very Low'),('2','Low'),('3','medium'),('4','High'), ('5','Very High')],'Previous Experience with Cilent')
    worth_client = fields.Selection([('1','Very Low'),('2','Low'),('3','medium'),('4','High'), ('5','Very High')],'Worthiness of the Cilent')
    serious_enquiry = fields.Selection([('1','Poor'),('2','Average'),('3','Good'),('4','Very Good'), ('5','Excellent')],'Seriousness of the Enquiry')
    budget_enquiry = fields.Selection([('1','Poor'),('2','Average'),('3','Good'),('4','Very Good'), ('5','Excellent')],'Budgetory or Firm Enquiry')
    feedback = fields.Text("FeedBack")
    analysis = fields.Text("Note")
    analysis_document = fields.Binary('Root Cause Analysis')

    
class source_name(models.Model):
    _name = 'source.name'

    name = fields.Char('Name')

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    man_hours = fields.Char('Man Days')

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    man_hours = fields.Char('Man Days')