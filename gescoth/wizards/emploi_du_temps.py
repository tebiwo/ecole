# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GescothEmploiWizard(models.TransientModel):
    _name = 'gescoth.emploi.wizard'
    _description = 'Emploi du temps'

    type_emploi_du_temp = fields.Selection([
        ('0', 'Professeur'),
        ('1', 'Classe'),
        ])
    professeur_id = fields.Many2one(
        'gescoth.professeur',
        string='Professeur',
    )
    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Classe',
        
        )
    annee_scolaire_id = fields.Many2one(
		'gescoth.anneescolaire',
		required=True,
		string="Année scolaire",
		default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
	)

    def imprimer_emploi_du_temps(self):
        data = {}
        list_emplois = []
        horaire_ids = self.env['gescoth.horaire'].search([])
        emploi_ids = self.env['gescoth.emploi.temps'].search([('classe_id','=', self.classe_id.id),('annee_scolaire_id','=',self.annee_scolaire_id.id)])
        for emploi in emploi_ids:
            vals = {
                'id': emploi.id,
                'jour' : emploi.jour,
                'classe_id' : emploi.classe_id,
                'professeur_id' : emploi.professeur_id,
                'matiere_id' : emploi.matiere_id,
                'annee_scolaire_id' : emploi.annee_scolaire_id,
                'horaire_id' : emploi.horaire_id,
                'heure_debut' : emploi.heure_debut,
                'heure_fin' : emploi.heure_fin,
            }
            list_emplois.append(vals)
        listehoraire = []
        for horaire in horaire_ids:
            vals ={
                'id': horaire.id,
                'name': horaire.name,
                'heure_debut': horaire.heure_debut,
                'heure_fin': horaire.heure_fin,
                'lundi':{
                    'matiere':'',
                    'professeur':'',
                },
                'mardi':{
                    'matiere':'',
                    'professeur':'',
                },
                'mercredi':{
                    'matiere':'',
                    'professeur':'',
                },
                'jeudi':{
                    'matiere':'',
                    'professeur':'',
                },
                'vendredi':{
                    'matiere':'',
                    'professeur':'',
                },
            }
            listehoraire.append(vals)
        
        for em in emploi_ids:
            for h in listehoraire:
                if em.jour == 'lundi' and h['id'] == em.horaire_id.id:
                    h['lundi']['matiere'] = em.matiere_id.name
                    h['lundi']['professeur'] = em.professeur_id.name

                if em.jour == 'mardi' and h['id'] == em.horaire_id.id:
                    h['mardi']['matiere'] = em.matiere_id.name
                    h['mardi']['professeur'] = em.professeur_id.name

                if em.jour == 'mercredi' and h['id'] == em.horaire_id.id:
                    h['mercredi']['matiere'] = em.matiere_id.name
                    h['mercredi']['professeur'] = em.professeur_id.name

                if em.jour == 'jeudi' and h['id'] == em.horaire_id.id:
                    h['jeudi']['matiere'] = em.matiere_id.name
                    h['jeudi']['professeur'] = em.professeur_id.name

                if em.jour == 'vendredi' and h['id'] == em.horaire_id.id:
                    h['vendredi']['matiere'] = em.matiere_id.name
                    h['vendredi']['professeur'] = em.professeur_id.name
                    

        data['listehoraire'] = listehoraire
        data['classe'] = self.classe_id.name
        data['annee'] = self.annee_scolaire_id.name
        return self.env.ref('gescoth.emploi_du_temps_report_view').report_action(self, data=data)
