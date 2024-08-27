# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools 
from odoo.exceptions import UserError, ValidationError


class GescothSaiseNoteWizard(models.TransientModel):

    _name = 'gescoth.saise.note.wizard'
    _description = 'Saise de note'

    classe_id = fields.Many2one(
        'gescoth.classe',
        string='classe',
        required=True, 
        )
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
    coeficient_id = fields.Many2one('gescoth.coeficient',required=True, string="Matière",)

    @api.onchange('classe_id')
    def _get_self_coef_ids(self):
        for rec in self:
            return {'domain':{'coeficient_id':[('name','=',self.classe_id.id)]}}

    def confirmer_saisie(self):
        matiere = self.env['gescoth.coeficient'].search([
            ('id','=', self.coeficient_id.id),
            ('professeur_id.user_id','=', self.env.uid)
        ])
        if not matiere :
            raise UserError(_('Vous n\'êtes pas autorisé à saisir ces notes ! Veuillez contactez votre administrateur'))
        
        return{
			'name':('Notes de ' + self.classe_id.name + ' - ' + self.annee_scolaire.name + ' - ' + self.saison + ' - ' + self.coeficient_id.matiere.name),
			'domain':[
                ('classe_id','=', self.classe_id.id),
                ('annee_scolaire','=', self.annee_scolaire.id),
                ('saison','=', self.saison),
                ('coeficient_id','=',self.coeficient_id.id),
            ],
			'res_model':'gescoth.note',
			'view_id':False,
			'view_mode':'tree,form',
			'type':'ir.actions.act_window',
		}