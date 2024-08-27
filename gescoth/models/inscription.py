# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GescothEleveInscription(models.Model):

    _name = 'gescoth.eleve.inscription'
    _description = 'Inscription'

    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Annee Scolaire',
        required=True
        )
    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Classe',
        required=True,
    )

    eleve_id = fields.Many2one(
        'gescoth.eleve',
        string='Elève',
        required=True,
    )

    date_inscription = fields.Date(string="Date d'inscription")

