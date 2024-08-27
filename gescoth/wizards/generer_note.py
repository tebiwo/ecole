# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GescothAbsence(models.TransientModel):
	_name = 'gescoth.generer.note'
	_description = "Générer les note note à saisir"

	classe_id = fields.Many2one(
		'gescoth.classe', 
		string='classe', 
		required=True,)
	annee_scolaire = fields.Many2one(
		'gescoth.anneescolaire', 
		required=True, 
		string="Année scolaire",
		default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
	)
	saison = fields.Selection([
		('s1','Semestre 1 - Trimestre 1'),
		('s2','Semestre 2 - Trimestre 2'),
		('s3','Semestre 3 - Trimestre 3')
		], 
		required=True,
	)

	def generer_note_a_saisir(self):
		eleve_ids = self.env['gescoth.eleve.inscription'].search([
			('classe_id','=', self.classe_id.id),
			('annee_scolaire_id','=', self.annee_scolaire.id)
		])
		# raise ValidationError(_(eleve_ids))
		# eleve_ids = self.env['gescoth.eleve'].search([('classe','=',self.classe_id.id)])
		if len(eleve_ids) == 0:
			raise ValidationError(_("Pas encore d'élève dans cette classe : " + self.classe_id.name))
		for eleve in eleve_ids:
			for coef in self.classe_id.coeficient_ids:
				vals = {
				'eleve_id':eleve.eleve_id.id,
				'classe_id':self.classe_id.id,
				'coeficient_id':coef.id,
				'saison':self.saison,
				'annee_scolaire':self.annee_scolaire.id,
				}
				note = self.env['gescoth.note'].search([
					('eleve_id','=', vals['eleve_id']),
					('classe_id','=', vals['classe_id']),
					('coeficient_id','=', vals['coeficient_id']),
					('saison','=', vals['saison']),
					('annee_scolaire','=', vals['annee_scolaire']),
				], limit=1)
				if not note:
					self.env['gescoth.note'].create(vals)