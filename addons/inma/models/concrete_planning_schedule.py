import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from datetime import datetime, date, time, timedelta

import base64
import sys
import os

import StringIO
import base64
from xlwt import *
from __builtin__ import True
from email import _name

try:
    import cStringIO as StringIO
    import xlwt
except:
    raise osv.except_osv('Warning !','python-xlwt module missing. Please install it.')


class DailyPlanningSchedule(models.Model):
	_name = "daily.planning.schedule"
	
	concrete_planning_ids = fields.One2many("concrete.planning","daily_plan_id", "Concrete Schedule")
	actual_planning_ids = fields.One2many("actual.planning","daily_plan_id", "Actual Concrete Schedule")
	#manufacturing_ids = fields.One2many("mrp.production","daily_plan_id", "Manufacturing")
	name = fields.Date("Date")
	shift_count = fields.Integer("Shift Count")
	location_id = fields.Many2one('stock.location','Location')
	project_id = fields.Many2one('project.name', 'Project Name')
	daily_plan_state = fields.Selection([('pending', 'Pending'),('ready', 'Ready'),('progress', 'In Progress'),('done', 'Finished')], string='Status', default='pending', track_visibility='onchange')
	shiftorder_count = fields.Integer('# Shift Schedule', compute='_compute_shiftorder_count')
	shiftorder_done_count = fields.Integer('# Done Shift Schedule', compute='_compute_shiftorder_done_count')
	
	_sql_constraints = [
        ('date_project_id_uniq', 'unique(name,project_id)', 'Already data created in same date'),
        ]
	
	@api.model
	def create(self,values):
		values['daily_plan_state'] = 'ready'
		return super(DailyPlanningSchedule, self).create(values)
	
	@api.multi
	def button_shift_plan(self):
		concrete_plan = self.env['concrete.planning']
		actual_plan = self.env['actual.planning']
		if self.name and self.shift_count:
			for shift in range(1, self.shift_count+1):
				concrete_plan.create({
					'plan_date':self.name,
					'daily_plan_id':self.id,
					'concrete_plan_state':'progress',
					'project_id':self.project_id.id,
				})
				
				actual_plan.create({
					'plan_date':self.name,
					'daily_plan_id':self.id,
					'concrete_plan_state':'progress',
					'project_id':self.project_id.id,
				})
				
			self.write({'daily_plan_state':'progress'})
		
	#@api.multi
	#def button_manufacturing(self):
		#production_id = self.env['mrp.production']
		#if self.name:
			#for production in range(6):
				#production_id.create({
				#'daily_plan_id':self.id,
				#'product_id':2,
				#'product_uom_id':[('category_id', '=', 1)],
				#'date_planned_start':datetime.now(),
				#})
	
	@api.multi
	@api.depends('concrete_planning_ids')
	def _compute_shiftorder_count(self):
		if self:
			data = self.env['concrete.planning'].read_group([('daily_plan_id', 'in', self.ids)], ['daily_plan_id'], ['daily_plan_id'])
			count_data = dict((item['daily_plan_id'][0], item['daily_plan_id_count']) for item in data)
			for shift in self:
				shift.shiftorder_count = count_data.get(shift.id, 0)
				
	@api.multi
	@api.depends('concrete_planning_ids.concrete_plan_state')
	def _compute_shiftorder_done_count(self):
		if self:
			data = self.env['concrete.planning'].read_group([('daily_plan_id', 'in', self.ids),('concrete_plan_state', '=', 'done')], ['daily_plan_id'], ['daily_plan_id'])
			count_data = dict((item['daily_plan_id'][0], item['daily_plan_id_count']) for item in data)
			for shift in self:
				shift.shiftorder_done_count = count_data.get(shift.id, 0)
			if self.shiftorder_count:
				if self.shiftorder_count == self.shiftorder_done_count:
					self.write({'daily_plan_state':'done'})

class concrete_planning(models.Model):
	_name="concrete.planning"
	
	plan_date = fields.Date('Date')
	name = fields.Many2one('shift.master','Shift')
	ring_count = fields.Integer("Ring Count")
	concrete_planning_schedule_ids = fields.One2many("concrete.planning.schedule","concrete_plan_id", "planning Schedule")		
	daily_planning_schedule_log = fields.One2many("daily.planning.schedule.log","concrete_planning_id", "Change Log")		
	daily_plan_id = fields.Many2one('daily.planning.schedule', "Daily Schedule Planning", index=True, ondelete='cascade', track_visibility='onchange')
	concrete_plan_state = fields.Selection([('progress', 'In Progress'),('done', 'Finished')], string='Status')
	file_f = fields.Binary("File", readonly=True)	
	file_name = fields.Char("File Name",size=128, readonly=True)
	project_id = fields.Many2one('project.name', 'Project Name')
	
	@api.onchange('ring_count')
	def onchange_ring_count(self):
		if self.ring_count:
			serial = 1
			planning_schedule_dict = []
			product_list = []
			for product_t in self.env['product.template'].search([('product_type','=','segment'),('active','=',True),('project_id','=',self.project_id.id)]):
				for product in self.env['product.product'].search([('product_tmpl_id','=',product_t.id)]):
					product_list.append(product.id)
			partial_ids = ()
			#find not completed ring ids
			actual_plan_ids = self.env['actual.planning'].search([('project_id','=',self.project_id.id)],order='id desc')
			for actual_plan in actual_plan_ids:
				if actual_plan.actual_concrete_schedule_ids:
					partial_ids = self.env['actual.concrete.schedule'].search([('actual_plan_id','=',actual_plan.id),('state','=','archived')])
					break

			ring_count_list = []
			if partial_ids:
				for partial in partial_ids:
					partial_segment_list = []
					for segment in partial.segment_id:
						partial_segment_list.append(segment.id)
					remain_segment_list = []
					for product in product_list:
						if product not in partial_segment_list:
							remain_segment_list.append(product)
					ring_count_list.append(partial.ring_id)
					planning_schedule_dict.append((0, 0, {'s_no': serial,'mould_id':partial.mould_id.id,'ring_id': partial.ring_id,'shift':self.name,'segment_id':remain_segment_list}))
					serial += 1

			#Ring id generation
			last_ring_id = ()
			actual_plan_ids = self.env['actual.planning'].search([('project_id','=',self.project_id.id)],order='plan_date desc')
			for actual_id in actual_plan_ids:
				if actual_id.actual_concrete_schedule_ids:
					last_ring_id = self.env['actual.concrete.schedule'].search([('actual_plan_id','=',actual_id.id),('state','=','done')],order='id desc', limit=1)
					break
			if last_ring_id:
				
				ring_count = last_ring_id.ring_id
				for count in range(1, self.ring_count+1):
					ring_count = int(ring_count) + 1
					
					if str(ring_count) not in ring_count_list:
						planning_schedule_dict.append((0, 0, {'s_no': serial, 'ring_id': str(ring_count),'shift':self.name,'segment_id':product_list}))
						serial += 1	
			else:
				for count in range(1, self.ring_count+1):
					planning_schedule_dict.append((0, 0, {'s_no': count, 'ring_id': count,'shift':self.name,'segment_id':product_list}))
							
			self.concrete_planning_schedule_ids = planning_schedule_dict
		
	@api.onchange('name')
	def onchange_shift_name(self):
		if self.name:
			same_shift = self.env['concrete.planning'].search([('plan_date','=',self.plan_date),('name','=',self.name.id), ('id','!=',self._origin.id),('project_id','=',self.project_id.id)])
			if same_shift:
				raise ValidationError(_("Given shift created for 1 time per day"))
				
	@api.constrains('name')
	def constrains_shift_name(self):
		if self.name:
			same_shift = self.env['concrete.planning'].search([('plan_date','=',self.plan_date),('name','=',self.name.id), ('id','!=',self.id),('project_id','=',self.project_id.id)])
			if same_shift:
				raise ValidationError(_("Given shift created for 1 time per day"))
			
	@api.one		
	def button_done(self):
		for record in self:
			daily_planning_schedule_log = [(0, 0, {'state_from': record.concrete_plan_state,'state_to': 'done','user_id': record._uid,'changed_on': datetime.now()
                })]
		record.write({'concrete_plan_state': 'done', 'daily_planning_schedule_log': daily_planning_schedule_log})
		
	@api.multi
	def button_reset(self):
	        for record in self:
			daily_planning_schedule_log = [(0, 0, {
				'state_from': record.concrete_plan_state,
				'state_to': 'progress',
				'user_id': record._uid,
				'changed_on': datetime.now()
                		})]
		record.write({'concrete_plan_state': 'progress', 'daily_planning_schedule_log': daily_planning_schedule_log})
		
	@api.multi
	def concrete_schedule_report(self):
		if self:
		#if self.plan_date and self.name and self.concrete_planning_schedule_ids:
			wbk = xlwt.Workbook()
			
			borders = xlwt.Borders()
			borders.left = xlwt.Borders.THIN
			borders.right = xlwt.Borders.THIN
			borders.top = xlwt.Borders.THIN
			borders.bottom = xlwt.Borders.THIN
			
			style_header = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 12*0x14
			style_header.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header.alignment = al1
			style_header.pattern = pat2
			style_header.borders = borders
			
			style_header_center = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_center.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_center.alignment = al1
			style_header_center.pattern = pat2
			style_header_center.borders = borders
			
			style_center_align = XFStyle()
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align.alignment = al_c
			style_center_align.borders = borders
			
			sheet1 = wbk.add_sheet('Concrete Planning Schedule')
			sheet1.portrait = False
			sheet1.col(0).width = 4000
			sheet1.col(1).width = 4000
			sheet1.col(2).width = 4000
			sheet1.col(3).width = 4000
			sheet1.col(4).width = 4000
			sheet1.col(5).width = 4000
			sheet1.col(6).width = 4000
			sheet1.col(7).width = 4000
			sheet1.col(8).width = 4000
			sheet1.col(9).width = 4000
			sheet1.col(10).width = 4000
			sheet1.col(11).width = 4000
			sheet1.col(12).width = 4000
			
			row = 0
			sheet1.row(0).height = 400
			sheet1.write_merge(row, row, 0, 13, 'Concrete Planning Schedule', style_header)
			row = 1
			sheet1.row(1).height = 300
			sheet1.row(2).height = 300
			sheet1.row(3).height = 400
			sheet1.write_merge(row, row, 0, 2, 'Date', style_header)
			sheet1.write_merge(row, row, 3, 6, self.plan_date, style_center_align)
			sheet1.write_merge(row, row, 7, 9, 'Shift', style_header)
			sheet1.write_merge(row, row, 10, 13, self.name.name, style_center_align)
			row = 2
			sheet1.write_merge(row, 3, 0, 0, 'S.No', style_header_center)
			sheet1.write_merge(row, 3, 1, 1, 'Ring ID', style_header_center)
			sheet1.write_merge(row, 3, 2, 2, 'Mould ID', style_header_center)
			sheet1.write_merge(row, 3, 3, 3, 'Segment', style_header_center)
			sheet1.write_merge(row, 3, 4, 4, 'Primary Demoulding Time', style_header_center)
			sheet1.write_merge(row, row, 5, 6, 'Cage Fixing Time', style_header_center)
			sheet1.write(3, 5, 'Start Time', style_header_center)
			sheet1.write(3, 6, 'End Time', style_header_center)
			sheet1.write_merge(row, row, 7, 8, 'Concrete', style_header_center)
			sheet1.write(3, 7, 'Start Time', style_header_center)
			sheet1.write(3, 8, 'End Time', style_header_center)
			sheet1.write_merge(row, 3, 9, 9, 'Finishing', style_header_center)
			sheet1.write_merge(row, row, 10, 11, 'Steam', style_header_center)
			sheet1.write(3, 10, 'Start Time', style_header_center)
			sheet1.write(3, 11, 'End Time', style_header_center)
			sheet1.write_merge(row, 3, 12, 12, 'Demoulding', style_header_center)
			sheet1.write_merge(row, 3, 13, 13, 'Remarks', style_header_center)
			row = 4
			for concrete_plan in self.concrete_planning_schedule_ids:
				sheet1.row(row).height = 400
				sheet1.write(row, 0, concrete_plan.s_no, style_center_align)
				sheet1.write(row, 1, concrete_plan.ring_id, style_center_align)
				sheet1.write(row, 2, str(concrete_plan.mould_id.name)+'/'+str((concrete_plan.mould_id.mould_type)).upper(), style_center_align)

				product_list = []

				for product in concrete_plan.segment_id:
					product_list.append(product.name + ",")
				sheet1.write(row, 3, product_list, style_center_align)
				sheet1.write(row, 4, concrete_plan.primary_demoulding_time, style_center_align)
				sheet1.write(row, 5, concrete_plan.cage_fixing_start_time, style_center_align)
				sheet1.write(row, 6, concrete_plan.cage_fixing_end_time, style_center_align)
				sheet1.write(row, 7, concrete_plan.concrete_start_time, style_center_align)
				sheet1.write(row, 8, concrete_plan.concrete_end_time, style_center_align)
				sheet1.write(row, 9, concrete_plan.finishing, style_center_align)
				sheet1.write(row, 10, concrete_plan.stream_start_time, style_center_align)
				sheet1.write(row, 11, concrete_plan.stream_end_time, style_center_align)
				sheet1.write(row, 12, concrete_plan.demoudling, style_center_align)
				sheet1.write(row, 13, concrete_plan.remarks, style_center_align)
				
				row += 1
			
			"""Parsing data as string """
			file_data = StringIO.StringIO()
			o=wbk.save(file_data)
			"""string encode of data in wksheet"""
			out = base64.encodestring(file_data.getvalue())
			"""returning the output xls as binary"""
			filename = 'concrete_planning_schedule.xls'
			self.write({'file_f':out, 'file_name':filename})
			return {

                   'url': '/inma/spreadsheet_report_controller/download_document?model=concrete.planning&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',

                   }
			
						
class concrete_planning_schedule(models.Model):
	_name="concrete.planning.schedule"
	
	s_no = fields.Integer("S.No")
	rfi_no = fields.Char("RFI No")
	ring_id = fields.Char("Ring ID")
	mould_id = fields.Many2one("mould.master","Mould ID")
	primary_demoulding_time = fields.Float("Primary Demoulding Time")
	cage_fixing_start_time = fields.Float("Cage Fixing Start Time")
	cage_fixing_end_time = fields.Float("Cage Fixing End Time")
	concrete_start_time = fields.Float("Concrete Start Time")
	concrete_end_time = fields.Float("Concrete End Time")
	finishing = fields.Float("Finishing")
	stream_start_time = fields.Float("Stream Start Time")
	stream_end_time = fields.Float("Stream End Time")
	demoudling = fields.Float("Demoulding")
	remarks = fields.Text("Remarks")
	shift = fields.Many2one('shift.master','Shift')
	concrete_plan_id = fields.Many2one('concrete.planning', "Concrete Planning", ondelete='cascade')
	segment_id = fields.Many2many('product.product','segment_product_plan_rel','product_id','plan_id','Segment')
        	
	@api.onchange('cage_fixing_start_time')
	def onchange_cage_fixing_start_time(self):
	 	if self.cage_fixing_start_time:
	 		transaction_schedule = self.env['daily.planning.transaction'].search([('state','=','active')])
	 		if transaction_schedule:
	 			self.cage_fixing_end_time = self.cage_fixing_start_time + transaction_schedule.cage_fix_period
	 			self.concrete_start_time = self.cage_fixing_end_time + transaction_schedule.concrete_start_period
	 			self.concrete_end_time = self.concrete_start_time + transaction_schedule.concrete_end_period
	 			self.finishing = self.concrete_end_time + transaction_schedule.finish_period
	 			self.stream_start_time = self.finishing + transaction_schedule.steam_start_period
	 			self.stream_end_time = self.stream_start_time + transaction_schedule.steam_end_period
	 			self.demoudling = self.stream_end_time + transaction_schedule.demoulding_period
	 		else:
	 			raise ValidationError(_("Please check any one daily transaction schedule record is active state"))
				
	@api.onchange('cage_fixing_end_time','concrete_start_time','concrete_end_time','finishing','stream_start_time','stream_end_time','demoudling')
	def onchange_time(self):
		if self.cage_fixing_end_time > 24:
			self.cage_fixing_end_time = self.cage_fixing_end_time - 24
		if self.concrete_start_time > 24:
			self.concrete_start_time = self.concrete_start_time - 24
		if self.concrete_end_time > 24:
			self.concrete_end_time = self.concrete_end_time - 24
		if self.finishing > 24:
			self.finishing = self.finishing - 24
		if self.stream_start_time > 24:
			self.stream_start_time = self.stream_start_time - 24
		if self.stream_end_time > 24:
			self.stream_end_time = self.stream_end_time - 24
		if self.demoudling > 24:
			self.demoudling = self.demoudling - 24

class actual_planning(models.Model):
	_name="actual.planning"
	
	plan_date = fields.Date('Date')
	name = fields.Many2one('shift.master','Shift')
	ring_count = fields.Integer("Ring Count")
	daily_plan_id = fields.Many2one('daily.planning.schedule', "Daily Schedule Planning", index=True, ondelete='cascade', track_visibility='onchange')
	actual_concrete_schedule_ids = fields.One2many("actual.concrete.schedule", "actual_plan_id", "Actual Concrete Schedule")
	daily_concrete_schedule_ids = fields.One2many("concrete.actual.planning", "actual_plan_id", "Daily Concrete Plannings")
	file_f = fields.Binary("File", readonly=True)	
	file_name = fields.Char("File Name",size=128, readonly=True)
	actual_plan_state = fields.Selection([('progress', 'In Progress'),('done', 'Finished')], string='Status')
	actual_planning_log = fields.One2many("actual.planning.log","actual_planning_id", "Change Log")
	file_f = fields.Binary("File", readonly=True)	
	file_name = fields.Char("File Name",size=128, readonly=True)	
	project_id = fields.Many2one('project.name', 'Project Name')

	@api.onchange('name')
	def onchange_shift(self):
		if self.name:
			concrete_plan_id = self.env['concrete.planning'].search([('plan_date','=',self.plan_date),('name','=',self.name.id),('concrete_plan_state','=','done'),('project_id','=',self.project_id.id)])
			if concrete_plan_id:
				self.ring_count = concrete_plan_id.ring_count
				ring_ids = self.env['concrete.planning.schedule'].search([('concrete_plan_id','=',concrete_plan_id.id)], order='id asc')
				actual_schedule_dict = []
				daily_concrete_dict = []
				count = 0
				for ring in ring_ids:
					count += 1
					segment_list = []
					for segment in ring.segment_id:
						segment_list.append(segment.id)
					actual_schedule_dict.append((0, 0, {'s_no': count, 'rfi_no':ring.rfi_no,'ring_id': ring.ring_id, 'mould_id':ring.mould_id.id, 'segment_id':segment_list}))
					daily_concrete_dict.append((0, 0, {'s_no': count, 'rfi_no':ring.rfi_no,'ring_id': ring.ring_id, 'mould_id':ring.mould_id.id, 'segment_id':segment_list,'primary_demoulding_time':ring.primary_demoulding_time,'cage_fixing_start_time':ring.cage_fixing_start_time,'cage_fixing_end_time':ring.cage_fixing_end_time,'concrete_start_time':ring.concrete_start_time,'concrete_end_time':ring.concrete_end_time,'finishing':ring.finishing,'stream_start_time':ring.stream_start_time,'stream_end_time':ring.stream_end_time,'demoudling':ring.demoudling,'remarks':ring.remarks}))
				self.actual_concrete_schedule_ids = actual_schedule_dict
				self.daily_concrete_schedule_ids = daily_concrete_dict
			else:
				raise ValidationError(_("First Create Concrete Planning for given shift"))
	
	@api.constrains('name')
	def constrains_shift(self):
		if self.name:
			concrete_plan_id = self.env['concrete.planning'].search([('plan_date','=',self.plan_date),('name','=',self.name.id),('concrete_plan_state','=','done')])
			if concrete_plan_id:
				return True
			else:
				raise ValidationError(_("First Create Concrete Planning for given shift"))
				
	@api.one		
	def button_done(self):
		for record in self:
			actual_planning_log = [(0, 0, {'state_from': record.actual_plan_state,'state_to': 'done','user_id': record._uid,'changed_on': datetime.now()
                })]
		record.write({'actual_plan_state': 'done', 'actual_planning_log': actual_planning_log})
		
	@api.multi
	def button_reset(self):
	        for record in self:
			actual_planning_log = [(0, 0, {
				'state_from': record.actual_plan_state,
				'state_to': 'progress',
				'user_id': record._uid,
				'changed_on': datetime.now()
                		})]
		record.write({'actual_plan_state': 'progress', 'actual_planning_log': actual_planning_log})


	@api.multi
	def actual_planning_report(self):
		if self:
		#if self.plan_date and self.name and self.actual_concrete_schedule_ids:
			wbk = xlwt.Workbook()
			
			borders = xlwt.Borders()
			borders.left = xlwt.Borders.THIN
			borders.right = xlwt.Borders.THIN
			borders.top = xlwt.Borders.THIN
			borders.bottom = xlwt.Borders.THIN
			
			style_header = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 12*0x14
			style_header.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header.alignment = al1
			style_header.pattern = pat2
			style_header.borders = borders
			
			style_header_center = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_center.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_center.alignment = al1
			style_header_center.pattern = pat2
			style_header_center.borders = borders
			
			style_center_align = XFStyle()
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align.alignment = al_c
			style_center_align.borders = borders
			
			sheet1 = wbk.add_sheet('Concrete Planning Schedule')
			sheet1.portrait = False
			sheet1.col(0).width = 4000
			sheet1.col(1).width = 4000
			sheet1.col(2).width = 4000
			sheet1.col(3).width = 4000
			sheet1.col(4).width = 4000
			sheet1.col(5).width = 4000
			sheet1.col(6).width = 4000
			sheet1.col(7).width = 4000
			sheet1.col(8).width = 4000
			sheet1.col(9).width = 4000
			sheet1.col(10).width = 4000
			sheet1.col(11).width = 4000
			sheet1.col(12).width = 4000
			
			row = 0
			sheet1.row(0).height = 400
			sheet1.write_merge(row, row, 0, 11, 'Actual Planning', style_header)
			row = 1
			sheet1.row(1).height = 300
			sheet1.row(2).height = 300
			sheet1.row(3).height = 400
			sheet1.write_merge(row, row, 0, 1, 'Date', style_header)
			sheet1.write_merge(row, row, 2, 4, self.plan_date, style_center_align)
			sheet1.write_merge(row, row, 5, 7, 'Shift', style_header)
			sheet1.write_merge(row, row, 8, 11, self.name.name, style_center_align)
			row = 2
			sheet1.write_merge(row, 3, 0, 0, 'S.No', style_header_center)
			sheet1.write_merge(row, 3, 1, 1, 'Ring ID', style_header_center)
			sheet1.write_merge(row, 3, 2, 2, 'Mould ID', style_header_center)
			sheet1.write_merge(row, 3, 3, 3, 'Segment', style_header_center)
			sheet1.write_merge(row, row, 4, 5, 'Cage Fixing Time', style_header_center)
			sheet1.write(3, 4, 'Start Time', style_header_center)
			sheet1.write(3, 5, 'End Time', style_header_center)
			sheet1.write_merge(row, 3, 6, 6, 'Finishing', style_header_center)
			sheet1.write_merge(row, row, 7, 8, 'Steam', style_header_center)
			sheet1.write(3, 7, 'Start Time', style_header_center)
			sheet1.write(3, 8, 'End Time', style_header_center)
			sheet1.write_merge(row, 3, 9, 9, 'Demoulding', style_header_center)
			sheet1.write_merge(row, 3, 10, 10, 'State', style_header_center)
			sheet1.write_merge(row, 3, 11, 11, 'Remarks', style_header_center)
			row = 4
			for concrete_plan in self.actual_concrete_schedule_ids:
				sheet1.row(row).height = 400
				sheet1.write(row, 0, concrete_plan.s_no, style_center_align)
				sheet1.write(row, 1, concrete_plan.ring_id, style_center_align)
				sheet1.write(row, 2, str(concrete_plan.mould_id.name)+'/'+str((concrete_plan.mould_id.mould_type)).upper(), style_center_align)
				product_list = []

				for product in concrete_plan.segment_id:
					product_list.append(product.name + ",")
				sheet1.write(row, 3, product_list, style_center_align)
				sheet1.write(row, 4, concrete_plan.concrete_start_time, style_center_align)
				sheet1.write(row, 5, concrete_plan.concrete_end_time, style_center_align)
				#sheet1.write(row, 6, concrete_plan.concrete_start_time, style_center_align)
				#sheet1.write(row, 7, concrete_plan.concrete_end_time, style_center_align)
				sheet1.write(row, 6, concrete_plan.finishing_time, style_center_align)
				sheet1.write(row, 7, concrete_plan.steam_start_time, style_center_align)
				sheet1.write(row, 8, concrete_plan.steam_end_time, style_center_align)
				sheet1.write(row, 9, concrete_plan.demoudling, style_center_align)
				sheet1.write(row, 10, concrete_plan.state, style_center_align)
				sheet1.write(row, 11, concrete_plan.remarks, style_center_align)
				
				row += 1
			
			"""Parsing data as string """
			file_data = StringIO.StringIO()
			o=wbk.save(file_data)
			"""string encode of data in wksheet"""
			out = base64.encodestring(file_data.getvalue())
			"""returning the output xls as binary"""
			filename = 'actual_concrete.xls'
			self.write({'file_f':out, 'file_name':filename})
			return {

                   'url': '/inma/spreadsheet_report_controller/download_document?model=actual.planning&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',

                   }
			
		
class actual_concrete_schedule(models.Model):
	_name="actual.concrete.schedule"
	
	s_no = fields.Integer("S.No")
	rfi_no = fields.Char("RFI No")
	ring_id = fields.Char("Ring ID")
	mould_id = fields.Many2one("mould.master","Mould ID")
	concrete_start_time = fields.Float("Start Time")
	concrete_end_time = fields.Float("End Time")
	finishing_time = fields.Float("Finishing Time")
	steam_start_time = fields.Float("Steam Start Time")
	steam_end_time = fields.Float("Steam End Time")
	demoudling = fields.Float("Demoulding")
	remarks = fields.Text("Remarks")
	state = fields.Selection([('done','Done'),('archived','Not Completed')])
	actual_plan_id = fields.Many2one('actual.planning', "Concrete Planning", ondelete='cascade')
	segment_id = fields.Many2many('product.product','segment_plan_rel','product_id','plan_id','Segment')
	mould_remarks = fields.Text('Mould Remarks')
	any_change = fields.Boolean('Any Change')

	
class mould_master(models.Model):
	_name="mould.master"
	
	name = fields.Char("Mould")
	mould_type = fields.Selection([('l','L'),('r','R')],'Type')
	
	@api.depends('name','mould_type')
	def name_get(self):
		result = []
		for mould in self:
			name = mould.name +'/'+ (mould.mould_type).upper()
			result.append((mould.id,name))
		return result

class shift_master(models.Model):
	_name = "shift.master"
	
	name = fields.Integer('Shift No')
	
	_sql_constraints = [
        ('name_uniq', 'unique(name)', 'Already same shift name created'),
        ]

class mould_casting(models.Model):
	_name = "mould.casting"

	date = fields.Date('Date')
	weather = fields.Many2one("weather","Weather")
	start_time = fields.Float("Start Time")
	close_time = fields.Float("Close Time")
	strength = fields.Integer("Strength")
	floor_incharge = fields.Many2one("hr.employee", "Floor Incharge")
	post_concrete_start_time = fields.Float("Post Concrete Start Time")
	post_concrete_close_time = fields.Float("Post Concrete Close Time")
	post_concrete_floor_incharge = fields.Many2one("hr.employee", "Post Concrete Floor Incharge")
	post_concrete_strength = fields.Integer("Post Concrete Strength")
	mould_casting_line_ids = fields.One2many('mould.casting.line','mould_casting_id','Mould Casting')
	
	@api.onchange('date')
	def onchange_date(self):
		if self.date:
			actual_plan_ids = self.env['actual.planning'].search([('plan_date','=',self.date)])
			actual_schedule = self.env['actual.concrete.schedule'].search([('actual_plan_id','in',actual_plan_ids.ids),('state','=','done')], order='ring_id asc')
			mould_casting_dict = []
			for actual in actual_schedule:
				lot_ids = self.env['stock.production.lot'].search([('name','=',actual.ring_id)])
				product_list = []
				for lot in lot_ids:
					product_list.append(lot.product_id.id)
				mould_casting_dict.append((0, 0, {'ring_id':actual.ring_id,'segment_ids':product_list, 'mould_id':actual.mould_id.id}))
			self.mould_casting_line_ids = mould_casting_dict
	
	@api.one
	@api.constrains('mould_casting_line_ids')
	def constraint_mould_casting(self):
		if self.mould_casting_line_ids:
			return True
		else:
			raise ValidationError(_("Enter Mould Casting Line"))
			
class mould_casting_line(models.Model):
	_name = "mould.casting.line"
	
	mould_casting_id = fields.Many2one('mould.casting','Mould Casting')
	ring_id = fields.Integer("Ring ID")
	mould_id = fields.Many2one("mould.master","Mould ID")
	segment_ids = fields.Many2many('product.product','mould_casting_line_product_rel','product_id','mould_casting_line_id', 'Segment')
	micro_finishing = fields.Char('Micro Finishing')
	ring_finishing = fields.Char('Ring Finishing')
	rfi_closing = fields.Char('RFI Finishing')
	
class mould_preparation(models.Model):
	_name = "mould.preparation"
	
	date = fields.Date("Date")
	start_time = fields.Float("Start Time")
	close_time = fields.Float("End Time")
	strength = fields.Integer("Strength")
	supervisor_name = fields.Many2one("hr.employee","Supervisor Name")
	mould_preparation_line_ids = fields.One2many('mould.preparation.line','mould_preparation_id','Mould Preparation Line')
	back_side_workers_ids = fields.One2many('back.side.workers','mould_preparation_id','Back Side Workers')
	file_f = fields.Binary("File", readonly=True)	
	file_name = fields.Char("File Name",size=128, readonly=True)
	
	@api.one
	@api.constrains('mould_preparation_line_ids', 'back_side_workers_ids')
	def constraint_mould_preparation(self):
		if self.mould_preparation_line_ids and self.back_side_workers_ids:
			return True
		else:
			raise ValidationError(_("Enter the value in Front side and Back side workers"))

	@api.multi
	def print_report(self):
		if self:
			wbk = xlwt.Workbook()
			borders = xlwt.Borders()
			borders.left = xlwt.Borders.THIN
			borders.right = xlwt.Borders.THIN
			borders.top = xlwt.Borders.THIN
			borders.bottom = xlwt.Borders.THIN
			
			style_header = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 12*0x14
			style_header.font = fnt        
			al1 = Alignment()
			al1.horz = Alignment.HORZ_CENTER
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header.alignment = al1
			style_header.pattern = pat2
			style_header.borders = borders
			
			style_header_left = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_left.font = fnt
			style_header_left.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_left.alignment = al1
			style_header_left.pattern = pat2
			style_header_left.borders = borders
			
			style_header_left1 = XFStyle()
			fnt = Font()
			fnt.bold = True
			fnt.height = 11*0x14
			style_header_left.font = fnt
			style_header_left.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_left1.alignment = al1
			style_header_left1.pattern = pat2
			
			style_header_left2 = XFStyle()
			fnt = Font()
			fnt.height = 11*0x14
			style_header_left.font = fnt
			style_header_left.font = fnt
			al1 = Alignment()
			al1.horz = Alignment.HORZ_LEFT
			al1.vert = Alignment.VERT_CENTER
			pat2 = Pattern()
			style_header_left2.alignment = al1
			style_header_left2.pattern = pat2
			style_header_left2.borders = borders
			
			style_center_align = XFStyle()
			fnt1 = Font()
			fnt1.bold = True
			fnt1.height = 11*0x14
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align.font = fnt1
			style_center_align.alignment = al_c
			
			style_center_align1 = XFStyle()
			fnt1 = Font()
			fnt1.bold = True
			fnt1.height = 11*0x14
			al_c = Alignment()
			al_c.horz = Alignment.HORZ_CENTER
			al_c.vert = Alignment.VERT_CENTER
			style_center_align1.font = fnt1
			style_center_align1.alignment = al_c
			style_center_align1.borders = borders
			
			sheet1 = wbk.add_sheet('Front Side')
			sheet1.portrait = False
			
			
			
			sheet1.col(0).width = 3000
			sheet1.col(1).width = 3000
			sheet1.col(2).width = 3000
			sheet1.col(3).width = 3000
			sheet1.col(4).width = 3000
			sheet1.col(5).width = 3000
			sheet1.col(6).width = 3000
			sheet1.col(7).width = 3000
			sheet1.col(8).width = 3000
			sheet1.col(9).width = 3000
			
			sheet1.row(0).height = 400
			row = 1
			sheet1.write_merge(row, row, 0, 10, 'Mould Preparation', style_header)

			row = 2
			sheet1.write(row, 0, 'Date', style_center_align1)
			sheet1.write(row, 1, self.date, style_header_left1)	
			sheet1.write(row, 2, 'Start Time', style_center_align1)
			sheet1.write(row, 3, self.start_time, style_header_left1)	
			sheet1.write(row, 4, 'End Time', style_center_align1)
			sheet1.write(row, 5, self.close_time, style_header_left1)
			sheet1.write(row, 6, 'Strength', style_center_align1)
			sheet1.write(row, 7, self.strength, style_header_left1)
			sheet1.write_merge(row, row, 8, 10, 'Supervisor Name:  '+self.supervisor_name.name, style_header_left1)

			i = 0
			row = 3
			sheet1.write_merge(row, 4, 0, 0, 'S.No', style_center_align1)						
			sheet1.write_merge(row, 4, 1, 1, 'Ring ID', style_center_align1)		
			sheet1.write_merge(row, 4, 2, 2, 'Mould ID', style_center_align1)		
			sheet1.write_merge(row, 4, 3, 3, 'Segment', style_center_align1)		
			sheet1.write_merge(row, row, 4, 5, 'Demoulding Time of Previous ring', style_center_align1)
			sheet1.write(4, 4, 'Approved', style_center_align1)
			sheet1.write(4, 5, 'Done', style_center_align1)
			sheet1.write_merge(row, row, 6, 6, 'Cleaning & Oiling', style_center_align1)
			sheet1.write(4, 6, 'Time & Pax.', style_center_align1)
			sheet1.write_merge(row, row, 7, 7, 'Cage fixing & Inserts', style_center_align1)
			sheet1.write(4, 7, 'Time & Pax.', style_center_align1)
			sheet1.write_merge(row, row, 8, 8, 'Ready for Concreting', style_center_align1)
			sheet1.write(4, 8, 'Time', style_center_align1)
			sheet1.write_merge(row, 4, 9, 10, 'Remarks', style_center_align1)
			row = 5
			for preparation_line in self.mould_preparation_line_ids:
			        i += 1
				sheet1.write(row, 0, i, style_header_left1)			
				sheet1.write(row, 1, preparation_line.ring_id, style_header_left1)
				sheet1.write(row, 2, str(preparation_line.mould_id.name)+'/'+str((preparation_line.mould_id.mould_type)).upper(), style_header_left1)
				sheet1.write(row, 3, preparation_line.segment_id.name, style_header_left1)
				sheet1.write(row, 4, preparation_line.demoudling_time_pre_ring_approx, style_header_left1)
                                sheet1.write(row, 5, preparation_line.demoudling_time_pre_ring_done, style_header_left1)				
				sheet1.write(row, 6, preparation_line.cleaning_oil_time, style_header_left1)
				sheet1.write(row, 7, preparation_line.cage_fixing_time, style_header_left1)
				sheet1.write(row, 8, preparation_line.concreting_time, style_header_left1)
				sheet1.write_merge(row, row, 9, 10, preparation_line.remarks, style_header_left1)
				row += 1
				
                        sheet2 = wbk.add_sheet('Back Side')
			sheet2.portrait = False		
			
			sheet2.col(0).width = 3000
			sheet2.col(1).width = 3000
			sheet2.col(2).width = 3000
			sheet2.col(3).width = 3000
			sheet2.col(4).width = 3000
			sheet2.col(5).width = 3000
			sheet2.col(6).width = 3000
			sheet2.col(7).width = 3000
			sheet2.col(8).width = 3000
			sheet2.col(9).width = 3000
			
			sheet2.row(0).height = 400
			i = 0
			row = 1
			sheet2.write(row, 0, 'S.No', style_center_align1)
			sheet2.write(row, 1, 'Name', style_center_align1)
			sheet2.write(row, 2, 'ID', style_center_align1)
			sheet2.write(row, 3, 'Work', style_center_align1)
			sheet2.write_merge(row, row, 4, 5, 'Time', style_center_align1)	
			sheet2.write(row, 6, 'Remarks', style_center_align1)
			row = 2
                        for back_side in self.back_side_workers_ids:
			        i += 1
				sheet2.write(row, 0, i, style_header_left1)			
				sheet2.write(row, 1, back_side.employee_id.name, style_header_left1)
				sheet2.write(row, 2, back_side.id_no, style_header_left1)	
				sheet2.write(row, 3, back_side.work, style_header_left1)				
				sheet2.write(row, 4, back_side.start_time, style_header_left1)				
				sheet2.write(row, 5, back_side.end_time, style_header_left1)				
				sheet2.write(row, 6, back_side.remarks, style_header_left1)		
				row += 1		
				
			"""Parsing data as string """
			file_data = StringIO.StringIO()
			o=wbk.save(file_data)
			"""string encode of data in wksheet"""
			out = base64.encodestring(file_data.getvalue())
			"""returning the output xls as binary"""
			filename = 'mould_preparation_report.xls'
			self.write({'file_f':out, 'file_name':filename})
			return {

                   'url': '/inma/spreadsheet_report_controller/download_document?model=mould.preparation&field=%s&id=%s&filename=%s'%(self.file_f,self.id,self.file_name),
                   'target': 'new',
                   'type': 'ir.actions.act_url',
                   }


class mould_preparation_line(models.Model):
	_name = "mould.preparation.line"
	
	ring_id = fields.Integer("Ring ID")
	mould_id = fields.Many2one("mould.master","Mould ID")
	segment_id = fields.Many2one('product.product','Segment')
	demoudling_time_pre_ring_approx = fields.Float("Previous ring time Approved")
	demoudling_time_pre_ring_done = fields.Float("Previous ring time Done")
	cleaning_oil_time = fields.Float('Cleaning oiling Time')
	cleaning_oil_pax = fields.Char('Cleaning oiling pax')
	cage_fixing_time = fields.Float('Cage fixing inserts Time')
	cage_fixing_pax = fields.Char('Cage fixing inserts Pax')
	concreting_time = fields.Float('Concreting Time')
	remarks = fields.Text('Remarks')
	mould_preparation_id = fields.Many2one('mould.preparation','Mould Preparation')
	
class back_side_workers(models.Model):
	_name = "back.side.workers"
	
	employee_id = fields.Many2one('hr.employee','Employee')
	id_no = fields.Char('ID')
	work = fields.Char('Work')
	start_time = fields.Float('Start Time')
	end_time = fields.Float('End Time')
	remarks = fields.Text('Remarks')
	mould_preparation_id = fields.Many2one('mould.preparation','Mould Preparation')
	
	@api.onchange('employee_id')
	def onchange_employee_id(self):
		if self.employee_id:
			self.id_no = self.employee_id.cid
			
class weather(models.Model):
	_name = "weather"
	
	name = fields.Char("Weather")

class special_events(models.Model):
	_name = "special.events"
	
	name = fields.Char("Special Event")
	
class daily_employee_workprogess(models.Model):
	_name = "daily.employee.workprogress"
	
	date = fields.Date("Date")
	day = fields.Char("Day")
	weather = fields.Many2one("weather","Weather")
	start = fields.Float("Start")
	lunch_break_from = fields.Float("Break Start")
	lunch_break_to = fields.Float("Break End")
	finish = fields.Float("Finish")
	special_event_ids = fields.Many2many('special.events','daily_workprogress_spl_evnt_rel','workprogress_id','special_event_id','Special Event')
	
	@api.onchange('date')
	def onchange_date(self):
		if self.date:
			week_day = datetime.strptime(self.date, "%Y-%m-%d").date().weekday()
			if week_day == 0:
				self.day = "Monday"
			elif week_day == 1:
				self.day = "Tuesday"
			elif week_day == 2:
				self.day = "Wednesday"
			elif week_day == 3:
				self.day = "Thursday"
			elif week_day == 4:
				self.day = "Friday"
			elif week_day == 5:
				self.day = "Saturday"
			else:
				self.day = "Sunday"
				
class daily_planning_transaction(models.Model):
	_name = "daily.planning.transaction"
	
	cage_fix_period = fields.Float('Cage Fix Period')
	concrete_start_period = fields.Float('Concrete Start Period')
	concrete_end_period = fields.Float('Concrete End Period')
	finish_period = fields.Float('Finishing Period')
	steam_start_period = fields.Float('Steam Start Period')
	steam_end_period = fields.Float('Steam End Period')
	demoulding_period = fields.Float('Demoulding Period')	
	state = fields.Selection([('active','Active'),('archived','Archived')], 'State', default='active')
	
	@api.model
	def create(self,vals):
		active_record = self.env['daily.planning.transaction'].search([('state','=','active')])
		if active_record:
			raise ValidationError(_("Already record is in active.Please Archive then create new record"))
		if vals.get('cage_fix_period') == 0 and vals.get('concrete_start_period') == 0 and vals.get('concrete_end_period') == 0 and vals.get('finish_period') == 0 and vals.get('steam_start_period') == 0 and vals.get('steam_end_period') == 0 and vals.get('demoulding_period') == 0:
			raise ValidationError(_("Enter hours periods in all fields"))
		return super(daily_planning_transaction, self).create(vals)
		
	@api.one
	def button_archived(self):
		self.state = 'archived'
		
class MrpProduction(models.Model):
	_inherit = "mrp.production"
	
	shift_id = fields.Many2one('shift.master','Shift')	
	#daily_plan_id = fields.Many2one('daily.planning.schedule', "Daily Schedule Planning", index=True, ondelete='cascade', track_visibility='onchange')

	@api.one
	@api.constrains('product_id','shift_id','date_planned_start','product_qty')
	def constraint_shift_qty(self):
		if self.product_id and self.shift_id:
			actual_plan_id = self.env['actual.planning'].search([('plan_date','=',datetime.strptime(self.date_planned_start, "%Y-%m-%d %H:%M:%S").date()),('name','=',self.shift_id.id)])
			product_count = 0
			for actual_schedule in self.env['actual.concrete.schedule'].search([('actual_plan_id','=',actual_plan_id.id)]):
				for product in actual_schedule.segment_id:
					if self.product_id.id == product.id:
						product_count += 1
			if product_count:
				if self.product_qty != product_count:
					raise ValidationError(_("Quantity to Produce value should less than or equal to Planned Quantity"))
			
class StockMove(models.Model):
	_inherit = "stock.move"

	@api.constrains('quantity_available', 'product_uom_qty')
	def constrain_move_raw_product(self):
		if self.quantity_available and self.product_uom_qty:
			if self.quantity_available < self.product_uom_qty:
				raise ValidationError(_("Production Quantity is less than the Available Quantity"))
				
class production_testing(models.Model):
	 _name = "production.testing"
	 
	 date = fields.Date('Date')
	 ring_master_id = fields.Many2one('ring.master','Ring ID')
	 permanant_ring_count = fields.Integer(compute='_get_ring_count',string='Permanant Ring')
	 temporary_ring_count = fields.Integer(compute='_get_ring_count',string='Temporary Ring')
	 approved_ring_count = fields.Integer(compute='_get_ring_count',string='Approved Ring')
	 dispatched_ring_count = fields.Integer(compute='_get_ring_count',string='Dispatched Ring')
	 production_testing_ids = fields.One2many('production.testing.line','production_testing_id','Production Testing')
	 project_id = fields.Many2one('project.name', 'Project Name') 

	 @api.onchange('date','project_id')
	 def onchange_date(self):
		 if self.date and self.project_id:
			actual_plan_ids = self.env['actual.planning'].search([('plan_date','=',self.date),('project_id','=',self.project_id.id)])
			actual_schedule = self.env['actual.concrete.schedule'].search([('actual_plan_id','in',actual_plan_ids.ids),('state','=','done')], order='ring_id asc')
			production_testing_dict = []
			for actual in actual_schedule:
				lot_ids = self.env['stock.production.lot'].search([('name','=',actual.ring_id)])
				product_list = []
				for lot in lot_ids:
					product_list.append(lot.product_id.id)
				production_testing_dict.append((0, 0, {'rfi_no':actual.rfi_no,'date':self.date,'ring_id':actual.ring_id,'segment_ids':product_list, 'mould_id':actual.mould_id.id}))
			self.production_testing_ids = production_testing_dict
			
	 @api.multi
	 @api.depends('permanant_ring_count','temporary_ring_count','approved_ring_count','dispatched_ring_count')
	 def _get_ring_count(self):
		 if self.production_testing_ids:
			 permanant_ring = 0
			 temporary_ring = 0
			 approved_ring = 0
			 dispatched_ring = 0
			 for permanant in self.production_testing_ids:
				 if permanant.permanent_ring:
					 permanant_ring += 1
				 if permanant.temporary_ring:
					 temporary_ring += 1
				 if permanant.approved_ring:
					 approved_ring += 1
				 if permanant.dispatched_ring:
					 dispatched_ring += 1
			 self.permanant_ring_count = permanant_ring
			 self.temporary_ring_count = temporary_ring
			 self.approved_ring_count = approved_ring
			 self.dispatched_ring_count = dispatched_ring
					
class ring_master(models.Model):
	_name = "ring.master"
	
	name = fields.Char("Name")
	
class production_testing_line(models.Model):
	_name = "production.testing.line"
	
	rfi_no = fields.Char('RFI No')
	date = fields.Date('Date')
	mould_id = fields.Many2one('mould.master',"Mould ID")
	ring_id = fields.Char("Ring")
	segment_ids = fields.Many2many('product.product','production_testing_line_product_rel','product_id','production_testing_line_id', 'Segment')
	permanent_ring = fields.Boolean("Permanant Ring")
	permanent_ref = fields.Char("Permanent Reference")
	temporary_ring = fields.Boolean("Temporary Ring")
	temporary_ref = fields.Char("Temporary Reference")
	approved_ring = fields.Boolean("Approved Ring")
	approved_ref = fields.Char("Approved Reference")
	approved_date = fields.Date("Approved Date")
	dispatched_ring = fields.Boolean("Dispatched Ring")
	dispatched_date = fields.Date("Dispatched Date")
	dispatched_ref = fields.Char("Dispatched Reference")
	micro_finishing = fields.Boolean("Micro Finishing")
	micro_finishing_date = fields.Date("Micro Finishing Date")
	micro_finishing_ref = fields.Char("Micro Finishing Reference")
	production_testing_id = fields.Many2one('production.testing','Production Testing')
	
class concrete_actual_planning(models.Model):
	_name="concrete.actual.planning"
	
	s_no = fields.Integer("S.No")
	rfi_no = fields.Char("RFI No")
	ring_id = fields.Char("Ring ID")
	mould_id = fields.Many2one("mould.master","Mould ID")
	primary_demoulding_time = fields.Float("Primary Demoulding Time")
	cage_fixing_start_time = fields.Float("Cage Fixing Start Time")
	cage_fixing_end_time = fields.Float("Cage Fixing End Time")
	concrete_start_time = fields.Float("Start Time")
	concrete_end_time = fields.Float("End Time")
	finishing = fields.Float("Finishing")
	stream_start_time = fields.Float("Start Time")
	stream_end_time = fields.Float("End Time")
	demoudling = fields.Float("Demoulding")
	remarks = fields.Text("Remarks")
	shift = fields.Many2one('shift.master','Shift')
	actual_plan_id = fields.Many2one('actual.planning', "Concrete Planning", ondelete='cascade')
	segment_id = fields.Many2many('product.product','segment_concrete_plan_rel','product_id','plan_id','Segment')

class daily_planning_schedule_log(models.Model):
	_name = "daily.planning.schedule.log"    
	_description = 'Change Log'
    
	user_id = fields.Many2one('res.users', 'Changed By', readonly=True)
	state_from = fields.Selection([('progress', 'In Progress'),('done', 'Finished')], 'From', readonly=True)
	state_to = fields.Selection([('progress', 'In Progress'),('done', 'Finished')], 'To', readonly=True)
	changed_on = fields.Datetime('Changed On', readonly=True)
	concrete_planning_id = fields.Many2one('concrete.planning', 'Change')
	
class actual_planning_log(models.Model):
	_name = "actual.planning.log"    
	_description = 'Change Log'
    
	user_id = fields.Many2one('res.users', 'Changed By', readonly=True)
	state_from = fields.Selection([('progress', 'In Progress'),('done', 'Finished')], 'From', readonly=True)
	state_to = fields.Selection([('progress', 'In Progress'),('done', 'Finished')], 'To', readonly=True)
	changed_on = fields.Datetime('Changed On', readonly=True)
	actual_planning_id = fields.Many2one('actual.planning', 'Change')
