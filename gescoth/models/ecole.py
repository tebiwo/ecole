# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

# classe pour gérer les matières
class GescothMatiere(models.Model):
	_name = 'gescoth.matiere'
	_description = 'Gestion des matière'
	_sql_constraints = [
	('name_uniq', 'unique (name)', _('Cette matière existe déjà !')),
	]

	name = fields.Char(string="Nom de la matière", required=True)
	nom_abrege = fields.Char(string="Nom abrégé")
	user_abrege = fields.Boolean(string="Utiliser le nom abrégé")
	group_id = fields.Many2one(
		'gescoth.matiere.groupe',
		string='Group',
		)
	type_matiere = fields.Selection([
		('theorie','Théorique'),
		('sport','Stportive')
	],
	string="Type de matière",
	default="theorie",
	required=True,)

class GescothMatiereGroupe(models.Model):

	_name = 'gescoth.matiere.groupe'
	_description = 'Groupe'

	name = fields.Char(string='Nom')



#classe pour ger les professeur
class GescothProfesseur(models.Model):
	_name = 'gescoth.professeur'
	_inherit = ['mail.thread','mail.activity.mixin']
	_description = 'Gestion des professeurs'

	name = fields.Char(string="Nom et prénoms", required=True, track_visibility='onchange')
	matricule = fields.Char(string="Matricule", track_visibility='onchange')
	photo = fields.Binary(string="Photo de l'élève")
	date_naissance = fields.Date(string="Date de naissance",track_visibility='onchange')
	lieu_naissance = fields.Char(string="Lieu de naissance", track_visibility='onchange')
	sexe = fields.Selection([('masculin','Masculin'),('feminin','Féminin')], string="Sexe")
	nationalite = fields.Many2one('res.country', string="Nationalité")
	telephone = fields.Char(string="Téléphone", track_visibility='onchange')
	email =  fields.Char(string="E-mail")
	adresse= fields.Text(string="Adresse complète")
	numero_carte = fields.Char(string="Numéro de CNI/Passport")
	salaire_base = fields.Float(string="Salaire de base")
	taux_horaire = fields.Float(string="Taux horaire pour les heures supplémentaires")
	date_service = fields.Date(
		string='Date de prise de service'
		)
	statut = fields.Selection([('volontaire','Volontaire'),('permanent','Permanent'),('partiel','Partiel')], string='Statut')
	matieres = fields.Many2many('gescoth.matiere', string="Matière enseignées")
	liste_emploi_du_temp_total= fields.Integer(
	    string='Total',
	    compute="_liste_emploi_du_temp"
	)
	heure_sup_ids = fields.One2many('gescoth.heure.suplementaire', 'professeur_id',string="Heures supplémentaire")
	emploi_ids = fields.One2many('gescoth.emploi.temps', 'professeur_id')
	user_id = fields.Many2one(
		'res.users',
		string='Utilisateur relié',
	)
	active = fields.Boolean(string="Active", default=True)
	
	def imprimer_attestion(self):
    		pass

	def liste_emploi_du_temp(self):
		return{
			'name':('Emploi du temps'),
			'domain':[('professeur_id','=', self.id),('annee_scolaire_id','=', int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')))],
			'res_model':'gescoth.emploi.temps',
			'view_id':False,
			'view_mode':'tree,form,kanban',
			'type':'ir.actions.act_window',
		}

	def _liste_emploi_du_temp(self):
		emplois = self.env['gescoth.emploi.temps'].search([('professeur_id','=',self.id),('annee_scolaire_id','=', int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')))])
		total =0
		for em in emplois:
			total +=1
		self.liste_emploi_du_temp_total = total
		


#classe pour gerer les classes
class GescothClasse(models.Model):
	_name = 'gescoth.classe'
	_description = 'Gestion des classes'
	_sql_constraints = [
	('name_uniq', 'unique (name)', _('Cette classe existe déjà !')),
	]

	name = fields.Char(string="Nom de la classe", required=True, index=True)
	description = fields.Char(string='Description')
	filiere = fields.Many2one('gescoth.filiere')
	professeur = fields.Many2one('gescoth.professeur', string="Professeur titulaire")
	coeficient_ids = fields.One2many('gescoth.coeficient', 'name', string="Coeficient de matières")
	moyenne_admission = fields.Float(string='Moyenne d\'admission', default=10)
	classe_id = fields.Many2one(
		'gescoth.classe',
		string='Classe supérieur',
	)
	eleve_ids =  fields.One2many('gescoth.eleve', 'classe', string="Liste des élèves")

	liste_des_eleves_total = fields.Integer(
	    string='Total',
	    compute="_liste_des_eleves_total"
	)
	liste_des_filles_total = fields.Integer(string="Total des filles", compute="_calucle_liste_des_filles")
	
	liste_des_garcons_total = fields.Integer(string="Total des garcons", compute="_calucle_liste_des_garcons")

	liste_des_autres_total = fields.Integer(string="Total des autres", compute="_calucle_liste_des_autres")


	niveau_id = fields.Many2one('gescoth.niveau', required=True)

	color = fields.Char(
        string="Color",
        help="Choose your color",
        size=7
    )
	total_matiere = fields.Integer(string="Total matière", compute="_compute_total_matiere")

	total_paiement = fields.Float(string="Total paiement", compute="_compute_total_paiement")

	def _compute_total_paiement(self):
		for rec in self:
			rec.total_paiement = rec.niveau_id.frais_total

	def _compute_total_matiere(self):
		for rec in self:
			total = 0
			for coeficient_id in rec.coeficient_ids:
				total += 1
			rec.total_matiere = total

	def _calucle_liste_des_filles(self):
		for rec in self:
			rec.liste_des_filles_total = len(self.env['gescoth.eleve'].search([('classe','=', rec.id),('sexe','=','feminin')]))
	
	def _calucle_liste_des_garcons(self):
		for rec in self:
			rec.liste_des_garcons_total = len(self.env['gescoth.eleve'].search([('classe','=', rec.id),('sexe','=','masculin')]))
	
	def _calucle_liste_des_autres(self):
		for rec in self:
			rec.liste_des_autres_total = len(self.env['gescoth.eleve'].search([('classe','=', rec.id),('sexe','!=','masculin'),('sexe','!=','feminin')]))
	

	def liste_des_autres(self):
		return{
			'name':('Elèves'),
			'domain':[('classe','=', self.id),('sexe','!=','masculin'),('sexe','!=','feminin')],
			'res_model':'gescoth.eleve',
			'view_id':False,
			'view_mode':'tree,form,kanban',
			'type':'ir.actions.act_window',
		}
	
	def liste_des_professeurs(self):
		return{
			'name':('Professeurs'),
			'domain':[('id','=', self.professeur.id)],
			'res_model':'gescoth.professeur',
			'view_id':False,
			'view_mode':'tree,form,kanban',
			'type':'ir.actions.act_window',
		}

	def nouvelle_eleve(self):
		return{
			'name':('Elèves'),
			'domain':[('classe','=', self.id)],
			'res_model':'gescoth.eleve',
			'view_id':False,
			'view_mode':'form',
			'type':'ir.actions.act_window',
		}
	
	def liste_des_matieres(self):
		return{
			'name':('Matières'),
			'domain':[('name','=', self.id)],
			'res_model':'gescoth.coeficient',
			'view_id':False,
			'view_mode':'tree,form,kanban',
			'type':'ir.actions.act_window',
		}

	def nouvelle_classe(self):
		return{
			'name':('Classe'),
			'res_model':'gescoth.classe',
			'domain':[('classe','=', self.id)],
			'view_id':False,
			'view_mode':'form',
			'type':'ir.actions.act_window',
		}

	def liste_des_garcons(self):
		return{
			'name':('Elèves garçons'),
			'domain':[('classe','=', self.id),('sexe','=','masculin')],
			'res_model':'gescoth.eleve',
			'view_id':False,
			'view_mode':'tree,form,kanban',
			'type':'ir.actions.act_window',
		}

	def liste_des_filles(self):
		return{
			'name':('Elèves filles'),
			'domain':[('classe','=', self.id),('sexe','=','feminin')],
			'res_model':'gescoth.eleve',
			'view_id':False,
			'view_mode':'tree,form,kanban',
			'type':'ir.actions.act_window',
		}



	def liste_des_eleves(self):
		return{
			'name':('Elèves de ' + self.name),
			'domain':[('classe','=', self.id)],
			'res_model':'gescoth.eleve',
			'view_id':False,
			'view_mode':'tree,form,kanban',
			'type':'ir.actions.act_window',
		}

	def _liste_des_eleves_total(self):
		for rec in self:
			rec.liste_des_eleves_total = len(self.env['gescoth.eleve'].search([('classe','=', rec.id)]))


class GescothFiliere(models.Model):
	_name = 'gescoth.filiere'
	_description = 'Gestion des filiere'
	_sql_constraints = [
	('name_uniq', 'unique (name)', _('Cette filiere existe déjà !')),
	]

	name = fields.Char(string="Nom de filiere", required=True)
	specialite = fields.Char(string="Spécialité")
	classe_ids = fields.One2many('gescoth.classe', 'filiere', string="Liste des classe")

class gescothHoraire(models.Model):
    _name = 'gescoth.horaire'
    _description = 'Horaire'

    name = fields.Char(
    	string='Horaire',
    	required=True,
    )
    heure_debut = fields.Float(
        string='Heure de début',
        required=True,
    )
    heure_fin = fields.Float(
        string='Heure de fin',
        required=True,
    )


class gescothEmploiTemps(models.Model):
    _name = 'gescoth.emploi.temps'
    _description = 'Emploi du temps'
    _rec_name = 'jour'

    jour = fields.Selection([
    	('lundi','lundi'),
    	('mardi','Mardi'),
    	('mercredi','Mercredi'),
    	('jeudi','Jeudi'),
    	('vendredi','Vendredi'),
    	('samedi','Samedi'),
    	('dimanche','Dimanche'),
    ], string="Jour", required=True,)

    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Classe',
        required=True,
    )
    professeur_id = fields.Many2one(
        'gescoth.professeur',
        string='Professeur',
        required=True,
    )
    matiere_id = fields.Many2one(
        'gescoth.matiere',
        string='Matière',
        required=True,
    )
    annee_scolaire_id = fields.Many2one(
		'gescoth.anneescolaire',
		string='Année scolaire',
		default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
	)
    horaire_id = fields.Many2one(
        'gescoth.horaire',
        string='Horaire',
    )
    heure_debut = fields.Float(
        string='Heure de début',
        # compute="_calculer_heure",
    )
    heure_fin = fields.Float(
        string='Heure de fin',
        # compute="_calculer_heure",
    )

    @api.onchange('horaire_id')
    def _onchange_horaire_id(self):
        for rec in self:
        	rec.heure_fin = rec.horaire_id.heure_fin
        	rec.heure_debut = rec.horaire_id.heure_debut

class GescothNiveau(models.Model):
    _name = 'gescoth.niveau'
    _description = 'Nieau'

    name = fields.Char(
    	string='Description',
    	required=True,
    )
    note = fields.Char(string="Note")
    frais_inscription = fields.Float(
        string="Frais d'inscription",
    )
    frais_formation = fields.Float(
        string="Frais de formation",
    )
    frais_internant = fields.Float(
        string="Frais d'internant",
    )
    frais_examen = fields.Float(
        string="Frais d'examen",
    )
    autres_frais = fields.Float(
        string="Autres frais",
    )
    classe_ids = fields.One2many(
        'gescoth.classe',
        'niveau_id',
        string='Classes',
    )

    frais_total = fields.Float(
        string="Frais total",
        compute= '_onchange_frais',
    )


    @api.onchange('frais_inscription','frais_formation','frais_internant','frais_internant','frais_examen','autres_frais')
    def _onchange_frais(self):
        for rec in self:
            rec.frais_total = rec.frais_inscription + rec.frais_formation + rec.frais_internant + rec.frais_examen + rec.autres_frais

class GescothEvenement(models.Model):

	_name = 'gescoth.evenement'
	_inherit = ['mail.thread','mail.activity.mixin']
	_description = 'Evénement'

	name = fields.Char(string="Nom de l'évènement", required=True)
	date_debut = fields.Date(string="Date de début", required=True)
	date_fin = fields.Date(string="Date de fin", required=True)
	maxi_personne = fields.Integer(string="Maximum de participant")
	personnel_id = fields.Many2one(
		'gescoth.personnel',
		string='Organisateur',
	)
	nombre_limite = fields.Boolean(string="Le nombre de personnes est limité")
	nombre_peronne = fields.Integer(string="nombre de personne")
	participant_ids = fields.One2many('gescoth.enevement.participant', 'evement_id',
	string="Liste des participants")

class GescothEnevementParticipant(models.Model):

	_name = 'gescoth.enevement.participant'
	_description = 'Participant'
	_rec_name = "eleve_id"

	eleve_id = fields.Many2one(
		'gescoth.eleve',
		string='Elève',
		required=True,
	)
	date_inscription = fields.Date(string="Date d'inscription",)
	evement_id = fields.Many2one(
		'gescoth.evenement',
		string='Evénement',
	)

class GescothHeureSuplementaire(models.Model):
    
	_name = 'gescoth.heure.suplementaire'
	_description = 'Heure suplémentaire'

	professeur_id = fields.Many2one(
		'gescoth.professeur',
		string='Professeur',
		)
	annee_scolaire_id = fields.Many2one(
		'gescoth.anneescolaire',
		string='Année scolaire',
		default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
	)
	date_heure_sup = fields.Date(string="Date")
	nombre_heure = fields.Float(string="Nombre d'heure", default=2)
	moi_paie = fields.Selection([
		('0', 'Janvier'),
		('1', 'Février'),
		('2', 'Mars'),
		('3', 'Avril'),
		('4', 'Mai'),
		('5', 'Juin'),
		('6', 'Juillet'),
		('7', 'Août'),
		('8', 'Septembre'),
		('9', 'Octobre'),
		('10', 'Novembre'),
		('11', 'Décembre'),
	], string="Mois de paie")
	
	classe_id = fields.Many2one(
		'gescoth.classe',
		string='Classe',
		)
