# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GescothAbsence(models.TransientModel):
	_name = 'gescoth.liste.eleve'
	_description = "Impression des liste d'élève"

	classe_id = fields.Many2one('gescoth.classe', string='classe', required=True,)
	annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire',
        required=True,
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )

	def imprimer_liste_eleve(self):
		data = {}
		liste_des_eleves = []
		eleves_inscrits = self.env['gescoth.eleve.inscription'].search([('classe_id','=',self.classe_id.id), ('annee_scolaire_id','=', self.annee_scolaire_id.id)])
		eleves_inscrits = eleves_inscrits.sorted(lambda line: line.eleve_id.nom_eleve)
		for inscrit in eleves_inscrits:
			vals ={
			'matricule':inscrit.eleve_id.name,
			'nom_eleve' : inscrit.eleve_id.nom_eleve,
            'photo' : inscrit.eleve_id.photo,
            'date_naissance' : inscrit.eleve_id.date_naissance,
            'lieu_naissance' : inscrit.eleve_id.lieu_naissance,
            'sexe' : inscrit.eleve_id.sexe,
            'nationalite' : inscrit.eleve_id.nationalite,
            'classe' : inscrit.eleve_id.classe.name,
            'statut' : inscrit.eleve_id.statut,
            'Apt_sport' : inscrit.eleve_id.Apt_sport,
			}
			liste_des_eleves.append(vals)
		data['liste_des_eleves']= liste_des_eleves
		return self.env.ref('gescoth.liste_eleve_report_view').report_action(self, data=data)