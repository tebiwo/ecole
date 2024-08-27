# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GescothEmploiWizard(models.TransientModel):
    _name = 'gescoth.emploi.prof.wizard'
    _description = 'Emploi du temps'

    professeur_id = fields.Many2one(
        'gescoth.professeur',
        string='Professeur',
    )
    annee_scolaire_id = fields.Many2one(
		'gescoth.anneescolaire',
		required=True,
		string="Année scolaire",
		default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
	)

    def imprimer_emploi_du_temps_prof(self):
        data = {}
        list_emplois = []
        horaire_ids = self.env['gescoth.horaire'].search([])
        emploi_ids = self.env['gescoth.emploi.temps'].search([('professeur_id','=', self.professeur_id.id),('annee_scolaire_id','=',self.annee_scolaire_id.id)])
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
                    'classe':'',
                },
                'mardi':{
                    'matiere':'',
                    'classe':'',
                },
                'mercredi':{
                    'matiere':'',
                    'classe':'',
                },
                'jeudi':{
                    'matiere':'',
                    'classe':'',
                },
                'vendredi':{
                    'matiere':'',
                    'classe':'',
                },
            }
            listehoraire.append(vals)
        
        for em in emploi_ids:
            for h in listehoraire:
                if em.jour == 'lundi' and h['id'] == em.horaire_id.id:
                    h['lundi']['matiere'] = em.matiere_id.name
                    h['lundi']['classe'] = em.classe_id.name

                if em.jour == 'mardi' and h['id'] == em.horaire_id.id:
                    h['mardi']['matiere'] = em.matiere_id.name
                    h['mardi']['classe'] = em.classe_id.name

                if em.jour == 'mercredi' and h['id'] == em.horaire_id.id:
                    h['mercredi']['matiere'] = em.matiere_id.name
                    h['mercredi']['classe'] = em.classe_id.name

                if em.jour == 'jeudi' and h['id'] == em.horaire_id.id:
                    h['jeudi']['matiere'] = em.matiere_id.name
                    h['jeudi']['classe'] = em.classe_id.name

                if em.jour == 'vendredi' and h['id'] == em.horaire_id.id:
                    h['vendredi']['matiere'] = em.matiere_id.name
                    h['vendredi']['classe'] = em.classe_id.name
            

        data['listehoraire'] = listehoraire
        data['professeur'] = self.professeur_id.name
        data['annee'] = self.annee_scolaire_id.name
        return self.env.ref('gescoth.emploi_du_temps_report_prof_view').report_action(self, data=data)
