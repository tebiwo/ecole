# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import *
from odoo.exceptions import ValidationError

class GescothCloturerNote(models.TransientModel):

    _name = 'gescoth.cloturer.note'
    _description = 'Clôturer les notes'

    classe_ids = fields.Many2many('gescoth.classe', required=True)
    annee_scolaire = fields.Many2one('gescoth.anneescolaire',
    default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
	required=True, string="Année scolaire",)
    saison = fields.Selection([
    	('s1','Semestre 1 - Trimestre 1'),
    	('s2','Semestre 2 - Trimestre 2'),
    	('s3','Semestre 3 - Trimestre 3')
    ], 
    	required=True
    )
    note_ids = fields.Many2many('gescoth.note')
    
    @api.onchange('classe_ids','saison','annee_scolaire')
    def _get_notes(self):
        for rec in self:
            rec.note_ids = self.env['gescoth.note'].search([
                ('classe_id','in',rec.classe_ids.ids),
                ('annee_scolaire','=', rec.annee_scolaire.id),
                ('saison','=',rec.saison),
            ])
    

    def cloturer_note(self):
        for rec in self:
            for note in rec.note_ids:
                note.state = '1'