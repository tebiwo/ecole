# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import *
from odoo.exceptions import ValidationError

class GescothExamenDeliberation(models.TransientModel):
    _name = 'gescoth.examen.deliberation'
    _description = 'Délibération'

    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Classe',
        required=True,
    )
    moyenne = fields.Float(string='Moyenne d\'admission')
    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire prochaine',
        required=True,
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )

    annee_scolaire_en_cours_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire en cours',
        required=True,
    )

    classe_sup_id = fields.Many2one(
        'gescoth.classe',
        string='Classe supérieur',
        required=True,
    )
    nombre = fields.Selection(string='Nombre de sequence', selection=[('5', '5'),('6', '6')])
    result_ids = fields.Many2many('gescoth.examen.annuel.resultat', string="Resultat d'examen")
    ordre = fields.Boolean(string="Impression par ordre de mérite")
    @api.onchange('classe_id')
    def onchange_moyenne(self):
        for rec in self:
            rec.moyenne = rec.classe_id.moyenne_admission
    

    @api.onchange('classe_id','moyenne','nombre','annee_scolaire_en_cours_id')
    def get_exame_result(self):
        for rec in self:            
            rec.result_ids = [(5,0,0)]
            rec.result_ids = self.env['gescoth.examen.annuel.resultat'].search([
                ('classe_id','=', self.classe_id.id),
                ('annee_scolaire','=', self.annee_scolaire_en_cours_id.id),
                ('nombre','=', self.nombre),
            ]).ids
            for res in rec.result_ids:
                if rec.moyenne <= res.moyenne:
                    res.result = '0'
                else:
                    res.result = '1'
                

    def deliberer(self):
        for rec in self:
            notes = self.env['gescoth.note'].search([('classe_id','=', self.classe_id.id),('state','=','0')])
            if len(notes) > 0:
                raise ValidationError(_("Veuillez valider et clôturer d'abord toutes les notes de la classe " +  self.classe_id.name + ' !'))

            if rec.annee_scolaire_en_cours_id == rec.annee_scolaire_id:
                raise ValidationError(_("L'année en cours ne peut pas être égale à l'année prochaine ! \n Veuillez configurer l'année scolaire"))
            
            if rec.classe_id == rec.classe_sup_id:
                raise ValidationError(_("La classe en cours ne peut pas être égale à la classe supérieur!"))
            for result in rec.result_ids:
                if result.state == '0':
                    if result.moyenne >= rec.moyenne:
                        result.eleve_id.classe = rec.classe_sup_id.id
                    else:
                        result.eleve_id.classe = rec.classe_id.id
                    result.state = '1'
                else:
                    raise ValidationError(_('Résultat déjà validé'))


    
    def imprimer_resultat(self):
        data ={}
        resultats = []
        sort = self.ordre
        for line in self.result_ids.sorted(lambda line: line.moyenne, reverse=sort):
            vals={
                'matricule':line.eleve_id.name,
                'eleve_id':line.eleve_id.nom_eleve,
                'moyenne':line.moyenne,
                'rang':line.rang,
                'result':['admin','Ajourné'][int(line.result)],
            }
            resultats.append(vals)
        data['resultats'] = resultats
        return self.env.ref('gescoth.impression_resultat_exament_report_view').report_action(self, data=data)