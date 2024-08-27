        # -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import *
import datetime

class GescothPayementEleve(models.Model):
    _name = 'gescoth.paiement.eleve'
    _description = 'Gestion des paiement des élèves'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'numer_recu'

    numer_recu = fields.Char(
        string="N° de reçu",
        readonly=True,
        required=True,
        copy=False,
        default='Nouveau',
        track_visibility='always',
    )

    eleve_id = fields.Many2one(
    	'gescoth.eleve',
    	string='Elève',
    	required=True,
    )
    date_paiement = fields.Date(
        string='Date de paiement',
        required=True,
        default=datetime.date.today(),
        track_visibility='always',
    )

    montant = fields.Float(
        string='Montant du paiement',
        required=True,
        track_visibility='onchange',
    )
    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Classe',
        store=True,
        required=True,
        track_visibility='always',
    )
    recu_manuel = fields.Char(string="N° du recu manuel")
    reste = fields.Float("Reste à payer", compute="_calucule_reste", 
    readonly=True 
    )
    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire',
        required=True,
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )
    responsable_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user.id,
        readonly=True,
    )
    tranche_ids = fields.Many2many('gescoth.tranche.line', string="Tranche à payer")

    @api.onchange('tranche_ids')
    def onchange_numero_tranche_id(self):
        for rec in self:
            total = 0
            for tranche in rec.tranche_ids:
                total += tranche.montant - tranche.montant_paye
            rec.montant = total
    
    
    @api.onchange('eleve_id')
    def onchange_eleve_id(self):
        return {'domain':{'tranche_ids':[
            ('eleve_id','=',self.eleve_id.id),
            ('tranche_id.state','=', 'confirmed'),
            ('state','in', ['0','1']),
        ]}}
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('accounted', 'Comptabilisée'),
        ('cancel', 'Annulé'),
    ], default='draft', readonly=True, track_visibility='onchange',)

    def _calucule_reste(self):
        for rec in self:
            paiements = self.env['gescoth.paiement.eleve'].search([('eleve_id','=',rec.eleve_id.id)])
            total_paye = 0
            for p in paiements:
                total_paye += p.montant
            rec.reste = rec.eleve_id.niveau_id.frais_total - total_paye

    def confirmer_paiement(self):
        for rec in self:
            rec.state = 'confirmed'

    def comptabiliser_paiement(self):
        for rec in self:
            vals = {
                'date_comptable': datetime.datetime.today(),
                'libelle': rec.numer_recu + ' de ' + rec.eleve_id.name + ' ' + rec.eleve_id.nom_eleve,
                'montant_debit': rec.montant,
                'eleve_id':rec.eleve_id.id,
                'montant_credit': 0,
                'solde_caisse': rec.montant,
                'annee_scolaire_id': self.annee_scolaire_id.id,
            }
            self.env['gescoth.comptabilite'].create(vals)
            montant = rec.montant
            for tranche in rec.tranche_ids:
                if montant >= tranche.reste_a_payer:
                    tranche.montant_paye += tranche.reste_a_payer
                    montant = montant - tranche.reste_a_payer
                    tranche.reste_a_payer = 0
                    tranche.paiement_id = self.id,
                    tranche.state = '2'
                elif montant < tranche.montant:
                    tranche.montant_paye += montant
                    tranche.paiement_id = self.id,
                    tranche.reste_a_payer = tranche.reste_a_payer - montant
                    montant = montant - tranche.reste_a_payer
                    tranche.state = '1'
            rec.state = 'accounted'

    def annuler_payement(self):
        for rec in self:
            rec.state = 'cancel'

    def mettre_en_brouillon(self):
        for rec in self:
            rec.state = 'draft'

    def unlink(self):
        for rec in self:
            if rec.state in ['accounted','confirmed','cancel']:
                raise ValidationError(_('Les paiements en status comptabilisé, confirmé ou annulé ne peuvent pas être supprimer'))
            return super(GescothPayementEleve, self).unlink()


    def envoyer_carte_eleve(self):
        template_id= self.env.ref('gescoth.eleve_paiement_template').id
        template = self.env['mail.template'].browse(template_id)
        return template.send_mail(self.id, force_send=True)

    @api.onchange('eleve_id')
    def _onchange_eleve_id(self):
        for rec in self:
            rec.classe_id = rec.eleve_id.classe.id

    @api.model
    def create(self, vals):
        if vals.get('numer_recu', 'Nouveau') == 'Nouveau':
            vals['numer_recu'] = self.env['ir.sequence'].next_by_code(
                'gescoth.paiement.eleve') or 'Nouveau'
        result = super(GescothPayementEleve, self).create(vals)
        return result

class GescothTranche(models.Model):
    _name = 'gescoth.tranche'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Tranche'
    _rec_name = "eleve_id"

    eleve_id = fields.Many2one(
        'gescoth.eleve',
        string='Elève',
        required=True,
        track_visibility='always', default=datetime.date.today(),
    )
    date = fields.Date(
        string='Date',
        required=True,
        track_visibility='always'
    )
    montant = fields.Float(
        string='Montant',
        required=True,
        track_visibility='always',
    )
    montat_deja_paye = fields.Float(
        string='Montant déjà payé',
        track_visibility='always',
    )
    nombre = fields.Integer(
        string='Nombre de payement',
        default=5, required=True,
        track_visibility='always',
    )
    date_premier_tranche = fields.Date(string="Date de la première tranche", required=True, track_visibility='always',)
    line_ids = fields.One2many('gescoth.tranche.line','tranche_id', string="Linge de tranche", ondelete='cascade')
    total = fields.Float(string='Total', compute="calculer_total_a_payer")
   

    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire',
        required=True,
        default=lambda self: int(
            self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )
    paiement_total = fields.Float(string='Paiement total', compute="_calcule_paiement_total")
    state = fields.Selection([
        ('draft','Brouillon'),
        ('confirmed','Confirmé'),
        ('cancel','Annulé'),
        ], default="draft", string="Statut", readonly=True, track_visibility='onchange',)

    def _calcule_paiement_total(self):
        for rec in self:
            paiements = self.env['gescoth.paiement.eleve'].search([
                ('eleve_id','=', rec.eleve_id.id),
                ('annee_scolaire_id','=', rec.annee_scolaire_id.id)
            ])
            total = 0
            for paiement in paiements:
                total += paiement.montant
            rec.paiement_total = total

    def liste_des_des_paiements(self):
        return{
            'name':('Paiements'),
            'domain':[('eleve_id','=', self.eleve_id.id), ('annee_scolaire_id','=', self.annee_scolaire_id.id)],
            'res_model':'gescoth.paiement.eleve',
            'view_id':False,
            'view_mode':'tree,form',
            'type':'ir.actions.act_window',
        }
    @api.onchange('field')
    def calculer_total_a_payer(self):
        for rec in self:
            total = 0
            reste_a_payer = self.montant - self.montat_deja_paye
            for line in self.line_ids:
                total += line.montant
            rec.total = total
            
          
    @api.onchange('eleve_id')
    def _onchange_classe_id(self):
        for rec in self:
            rec.montant = rec.eleve_id.classe.niveau_id.frais_total

    def calculer_tranche(self):
        for rec in self:
            reste_a_payer = rec.montant - rec.montat_deja_paye
            traches = self.env['gescoth.tranche.line'].search([('tranche_id','=', rec.id)])
            for t in traches:
                t.unlink()
            my_date = rec.date_premier_tranche
            for n in range(0, rec.nombre):
                vals ={
                    'date_echeanche': my_date,
                    'montant': (reste_a_payer / rec.nombre),
                    'eleve_id':rec.eleve_id.id,
                    'tranche_id': rec.id,
                    'reste_a_payer':(reste_a_payer / rec.nombre),
                }
                my_date = my_date + timedelta(days=30)
                my_date = date(my_date.year, my_date.month, rec.date_premier_tranche.day)

                self.env['gescoth.tranche.line'].create(vals)


    def confirmer_tranche(self):
        for rec in self:
            if (rec.montant - rec.montat_deja_paye)!= rec.total:
                raise ValidationError(_('Le total à payer doit être égale au montant total des tranche'))
            for line in rec.line_ids:
                activity = {
                    'activity_type_id': 1,
                    'date_deadline': line.date_echeanche,
                    'user_id': rec._uid,
                    'res_id': rec.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'gescoth.tranche')]).id,
                }
                self.env['mail.activity'].create(activity)            
            rec.state = 'confirmed'


    def annuler_tranche(self):
        for rec in self:
            rec.state = 'cancel'

    def brouilln_tranche(self):
        for rec in self:
            rec.state = 'draft'

class GescothPaiementLine(models.Model):
    _name = 'gescoth.tranche.line'
    _description = 'Ligne de tranche'
    _rec_name="numero"

    numero = fields.Char(string='Numéro de tranche', readonly=True, required=True, copy=False, default='Nouveau')
    date_echeanche = fields.Date(string="Date d'échéance", required=True,)
    montant = fields.Float(string="Montant", required=True,)
    date_payement = fields.Date(string="Date de paiement", default=datetime.date.today(),)

    paiement_id = fields.Many2one(
        'gescoth.paiement.eleve',
        string='Référence paiement',
        )
    montant_paye = fields.Float(string='Montant payé')
    tranche_id = fields.Many2one(
        'gescoth.tranche',
        string='Tranche', required=True,
    )
    eleve_id = fields.Many2one(
        'gescoth.eleve',
        string='eleve',
    )
    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Classe', compute="_get_classe", store=True,
        )
    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire',
        required=True,
        default=lambda self: int(
            self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )
    reste_a_payer = fields.Float(string='Reste à payer')
    state = fields.Selection([
        ('0', 'Non payé'),
        ('1', 'Partiellement payé'),
        ('2', 'Payé'),
    ], default="0")

    def _get_classe(self):
        for rec in self:
            rec.classe_id = rec.eleve_id.classe

    @api.model
    def create(self, values):
        if values.get('numero', 'Nouveau') == 'Nouveau':
            values['numero'] = self.env['ir.sequence'].next_by_code(
                'gescoth.tranche.line') or 'Nouveau'
            result = super().create(values)
        return result

    def Payer_la_trache(self):
        vals = {
            'eleve_id': self.tranche_id.eleve_id.id,
            'date_paiement': self.date_payement,
            'montant': self.montant,
            'classe_id': self.tranche_id.eleve_id.classe.id,
            'annee_scolaire_id': self.tranche_id.annee_scolaire_id.id,
            'tranche_ids':[self.id],
        }        
        # paiements = self.env['gescoth.paiement.eleve'].search([('tranche_ids','in', self.id)])
        # if paiements :
        #     return{
        #         'name':('Paiements'),
        #         'domain':[('id','=',self.id)],
        #         'res_model':'gescoth.paiement.eleve',
        #         'view_id':False,
        #         'view_mode':'form',
        #         'type':'ir.actions.act_window',
        #     }
            # raise ValidationError(_('Ce paiement existe déjà'))
        return self.env['gescoth.paiement.eleve'].create(vals)



class GescothDepense(models.Model):
    _name = 'gescoth.depense'
    _description = 'Dépense'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Libellé',
        required=True,
    )
    date_depense = fields.Date(
        string='Date',
        required=True,
        default=datetime.date.today(),
    )
    montant = fields.Float(string="Montant", required=True,)
    partenaire_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
    )
    responsable_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user.id,
        readonly=True,
    )
    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire',
        required=True,
        default=lambda self: int(
            self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confrimed', 'Confirmer'),
        ('canceled', 'Annuler'),
        ('accounted', 'Comptabilisée'),
    ], default="draft", string="Etat", readonly=True, track_visibility='onchange')

    def confirmer_recette(self):
        for rec in self:
            rec.state = 'confrimed'

    def comptabiliser_recette(self):
        for rec in self:
            vals = {
                'date_comptable': datetime.datetime.today(),
                'libelle': rec.name,
                'montant_debit': 0,
                'montant_credit': rec.montant,
                'solde_caisse': - rec.montant,
                'annee_scolaire_id': self.annee_scolaire_id.id,
            }
            self.env['gescoth.comptabilite'].create(vals)
            rec.state = 'accounted'

    def annuler_recette(self):
        for rec in self:
            rec.state = 'canceled'

    def mettre_brouillon_recette(self):
        for rec in self:
            rec.state = 'draft'

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'canceled'):
                raise ValidationError(
                    _('Vous ne pouve supprimer cet elément dans son état'))
        return models.Model.unlink(self)


class GescothRecette(models.Model):
    _name = 'gescoth.recette'
    _description = 'Recette'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Libellé',
        required=True,
    )
    date_depense = fields.Date(
        string='Date',
        required=True,
        default=datetime.date.today(),
    )
    montant = fields.Float(string="Montant", required=True,)
    partenaire_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
    )
    responsable_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user.id,
        readonly=True,
    )
    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire',
        required=True,
        default=lambda self: int(
            self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confrimed', 'Confirmer'),
        ('canceled', 'Annuler'),
        ('accounted', 'Comptabilisée'),
    ], default="draft", string="Etat", readonly=True, track_visibility='onchange')

    def confirmer_recette(self):
        for rec in self:
            rec.state = 'confrimed'

    def comptabiliser_recette(self):
        for rec in self:
            vals = {
                'date_comptable': datetime.datetime.today(),
                'libelle': rec.name,
                'montant_debit': rec.montant,
                'montant_credit': 0,
                'solde_caisse': rec.montant,
                'annee_scolaire_id': self.annee_scolaire_id.id,
            }
            self.env['gescoth.comptabilite'].create(vals)
            rec.state = 'accounted'

    def annuler_recette(self):
        for rec in self:
            rec.state = 'canceled'

    def mettre_brouillon_recette(self):
        for rec in self:
            rec.state = 'draft'

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'canceled'):
                raise ValidationError(
                    _('Vous ne pouve supprimer cet elément dans son état'))
        return models.Model.unlink(self)


class GescothProfPaiement(models.Model):

    _name = 'gescoth.prof.paiement'
    _description = 'Paiment de professeurs'
    _rec_name = 'professeur_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    professeur_id = fields.Many2one(
        'gescoth.professeur',
        string='Professeur',
        required=True,
    )
    date_paiement = fields.Date(
        string="Date de paiement", required=True, default=fields.Date.today)
    salaire_base = fields.Float(string="Salaire de base")
    heure_suplementaire = fields.Float(string="Heure supémentaire")
    montant_par_heure = fields.Float(string="Montant par heure")
    retenue_sur_paie = fields.Float(string="Retenue sur paie")
    note = fields.Text(string="Note")
    montant_heure_suplementaire = fields.Float(
        string="Montant Heure suplémentiare")
    montant_total = fields.Float(string="Montant total")
    mois = fields.Selection([
        ('1', 'Janvier'),
        ('2', 'Février'),
        ('3', 'Mars'),
        ('4', 'Avril'),
        ('5', 'Mai'),
        ('6', 'Juin'),
        ('7', 'Juillet'),
        ('8', 'Août'),
        ('9', 'Septembre'),
        ('10', 'Octobre'),
        ('11', 'Novembre'),
        ('12', 'Décembre'),
    ], required=True, string="Mois de paiement", default=datetime.datetime.now().strftime("%m"))
    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire',
        required=True,
        default=lambda self: int(
            self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confrimed', 'Confirmer'),
        ('canceled', 'Annuler'),
        ('accounted', 'Comptabilisée'),
    ], default="draft", string="Etat", readonly=True, track_visibility='onchange')

    @api.onchange('professeur_id',)
    def onchange_professeur_id(self):
        for rec in self:
            rec.salaire_base = rec.professeur_id.salaire_base
            rec.montant_par_heure = rec.professeur_id.taux_horaire

    @api.onchange('heure_suplementaire', 'montant_par_heure')
    def onchange_heure_sup(self):
        self.montant_heure_suplementaire = self.heure_suplementaire * self.montant_par_heure

    @api.onchange('retenue_sur_paie', 'salaire_base', 'heure_suplementaire', 'montant_par_heure', 'montant_heure_suplementaire', 'montant_total')
    def onchange_salarie_base(self):
        self.montant_total = self.salaire_base + \
            (self.heure_suplementaire * self.montant_par_heure) + \
            self.montant_heure_suplementaire - self.retenue_sur_paie

    def confirmer_paiement(self):
        for rec in self:
            rec.state = 'confrimed'

    def comptabiliser_paiement(self):
        for rec in self:
            vals = {
                'date_comptable': datetime.datetime.today(),
                'libelle': 'Paiement de salaire de ' + rec.professeur_id.name + ' pour ' + rec.mois,
                'montant_debit': 0,
                'montant_credit': rec.montant_total,
                'solde_caisse': - rec.montant_total,
                'annee_scolaire_id': self.annee_scolaire_id.id,
            }
            self.env['gescoth.comptabilite'].create(vals)
            rec.state = 'accounted'

    def annuler_paiement(self):
        for rec in self:
            rec.state = 'canceled'

    def mettre_brouillon_paiement(self):
        for rec in self:
            rec.state = 'draft'

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'canceled'):
                raise ValidationError(
                    _('Vous ne pouve supprimer cet elément dans son état'))
        return models.Model.unlink(self)


class GescothComptabilite(models.Model):
    
    _name = 'gescoth.comptabilite'
    _description = 'Comptabilité'
    _rec_name = 'libelle'

    date_comptable = fields.Date(string="Date comptable")
    libelle = fields.Char(string="Libellé")
    eleve_id = fields.Many2one(
        'gescoth.eleve',
        string='Elève',
        )
    montant_debit = fields.Float(string="Recette")
    montant_credit = fields.Float(string="Dépense")
    solde_caisse = fields.Float(
        string="solde caisse", compte="_compute_solde_caisse")
    annee_scolaire_id = fields.Many2one(
        'gescoth.anneescolaire',
        string='Année scolaire',
        required=True,
        default=lambda self: int(
            self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
    )

    @api.depends('montant_debit,montant_credi')
    def _compute_solde_caisse(self):
        for record in self:
            record.solde_caisse = record.montant_debit + record.montant_credit