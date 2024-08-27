# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class GescothAssistantInscription(models.TransientModel):
    _name = 'gescoth.assistant.inscription'
    _description = 'Assistant inscription des élèves'

    eleve_ids = fields.Many2many(
        'gescoth.eleve',
        string='Elèves',
    )
    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Nouvelle classe',
    )

    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire',
        required=True,
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )


    def inscrire_les_eleve(self):
        for rec in self:
            for eleve in rec.eleve_ids:
                vals = {
                    'annee_scolaire_id': self.classe_id.id,
                    'classe_id': self.classe_id.id,
                    'eleve_id': eleve.id,
                    'date_inscription': fields.Date.today()
                }
                inscrit  = self.env['gescoth.eleve.inscription'].search([
                    ('eleve_id','=', eleve.id),
                    ('annee_scolaire_id','=', rec.annee_scolaire_id.id),
                ], limit=1)
                if inscrit:
                    inscrit.classe_id = rec.classe_id,
                else:
                    self.env['gescoth.eleve.inscription'].create(vals)