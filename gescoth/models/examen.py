# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from .. functions.myFunctions import *
from datetime import datetime


class GescothExamenDeliberation(models.Model):

	_name = 'gescoth.examen.deliberation'
	_description = 'Délibération'

	annee_scolaire_id = fields.Many2one(
		'gescoth.anneescolaire',
		string='Annee Scolaire',
	)
	
# classe pour gérer les les coeficients
class GescothCoeficient(models.Model):
	_name = 'gescoth.coeficient'
	_description = 'Gestion des coeficient'
	_rec_name = 'matiere'

	name = fields.Many2one('gescoth.classe', string="Classe")
	matiere = fields.Many2one('gescoth.matiere', string="Matière", required=True)
	est_facultative = fields.Boolean(string="La matière est facultative")
	coef = fields.Float(string="Coeficient", default=1)
	professeur_id = fields.Many2one('gescoth.professeur','Professeur')
	
class GescothNoteAnnuelle(models.Model):

	_name = 'gescoth.note.annuelle'
	_description = 'Note par séquence annuelle'
	_rec_name = 'eleve_id'
	_order = 'eleve_id'

	eleve_id = fields.Many2one('gescoth.eleve', string="Elève", required=True)
	classe_id = fields.Many2one('gescoth.classe', string="Classe", required=True)
	coeficient_id = fields.Many2one('gescoth.coeficient', string="Matière", required=True)
	saison = fields.Selection([
		('s1','Semestre 1 - Trimestre 1'),
		('s2','Semestre 2 - Trimestre 2'),
		('s3','Semestre 3 - Trimestre 3')
		], 
		required=True,
	)
	note_sequence1 = fields.Float(string="Séquence 1", store=True,)
	s1_is_not_compose = fields.Boolean("N'a pas composé")
	note_sequence2 = fields.Float(string="Séquence 2", store=True,)
	s2_is_not_compose = fields.Boolean("N'a pas composé")
	note_sequence3 = fields.Float(string="Séquence 3", store=True,)
	s3_is_not_compose = fields.Boolean("N'a pas composé")
	note_sequence4 = fields.Float(string="Séquence 4", store=True,)
	s4_is_not_compose = fields.Boolean("N'a pas composé")
	note_sequence5 = fields.Float(string="Séquence 5", store=True,)
	s5_is_not_compose = fields.Boolean("N'a pas composé")
	note_sequence6 = fields.Float(string="Séquence 6", store=True,)
	s6_is_not_compose = fields.Boolean("N'a pas composé")

	total = fields.Float(string="Total", compute="_total")
	total_5 = fields.Float(string="Total", compute="_total_5")

	moyenne_annuel = fields.Float(string="Moyenne annuelle", compute="_moyenne_annuel")
	rang = fields.Char(string="Rang", compute="CalculerRang",)

	moyenne_annuel_5 = fields.Float(string="Moyenne annuelle", compute="_moyenne_annuel_5")
	rang_5 = fields.Char(string="Rang", compute="CalculerRang_5",)
	annee_scolaire = fields.Many2one('gescoth.anneescolaire', required=True, string="Année scolaire",)
	professeur_id = fields.Many2one('gescoth.professeur', "Professeur")
	appreciation = fields.Char(string='Appréciation', compute="_appreciation")
	appreciation_5 = fields.Char(string='Appréciation', compute="_appreciation_5")

	@api.onchange('moy_classe','note_compo')	    
	def _appreciation(self):
		appr = self.env['gescoth.appreciation'].search([])
		for rec in self:
			for ap in appr:
				if rec.moyenne_annuel >= ap.inf and rec.moyenne_annuel < ap.sup:
					rec.appreciation = ap.name
					return
				if rec.moyenne_annuel >= 20:
					rec.appreciation = 'Excellent'

	def CalculerRang(self):
		for rec in self:
			data = list()
			notes = self.env['gescoth.note.annuelle'].search([
				('classe_id','=', rec.classe_id.id),
				('saison','=', rec.saison),
				('coeficient_id','=', rec.coeficient_id.id),
			])
			for note in notes:
				data.append(note.moyenne_annuel)
			
			rec.rang = Rang(rec.moyenne_annuel, rec.eleve_id.sexe, data)

	def _moyenne_annuel(self):
		for rec in self:
			rec.moyenne_annuel = (rec.note_sequence1 + rec.note_sequence2 + rec.note_sequence3 + rec.note_sequence4 + rec.note_sequence5 + rec.note_sequence6)/6

	def _total(self):
		for rec in self:
			rec.total = rec.note_sequence1 + rec.note_sequence2 + rec.note_sequence3 + rec.note_sequence4 + rec.note_sequence5 + rec.note_sequence6


	@api.onchange('moy_classe','note_compo')	    
	def _appreciation_5(self):
		appr = self.env['gescoth.appreciation'].search([])
		for rec in self:
			for ap in appr:
				if rec.moyenne_annuel_5 >= ap.inf and rec.moyenne_annuel_5 < ap.sup:
					rec.appreciation_5 = ap.name
					return
				if rec.moyenne_annuel_5 >= 20:
					rec.appreciation_5 = 'Excellent'

	def CalculerRang_5(self):
		for rec in self:
			data = list()
			notes = self.env['gescoth.note.annuelle'].search([
				('classe_id','=', rec.classe_id.id),
				('saison','=', rec.saison),
				('coeficient_id','=', rec.coeficient_id.id),
			])
			for note in notes:
				data.append(note.moyenne_annuel_5)
			
			rec.rang_5 = Rang(rec.moyenne_annuel_5, rec.eleve_id.sexe, data)

	def _moyenne_annuel_5(self):
		for rec in self:
			rec.moyenne_annuel_5 = (rec.note_sequence1 + rec.note_sequence2 + rec.note_sequence3 + rec.note_sequence4 + rec.note_sequence5)/5

	def _total_5(self):
		for rec in self:
			rec.total_5 = rec.note_sequence1 + rec.note_sequence2 + rec.note_sequence3 + rec.note_sequence4 + rec.note_sequence5



class GesocthNote(models.Model):
	_name = 'gescoth.note'
	_description = 'Gestion des notes'
	_rec_name = 'eleve_id'
	_sql_constraints = [
		('saison_unique_note', 'UNIQUE (eleve_id, classe_id, coeficient_id, saison)', 'Cette note existe déjà !')
	]

	eleve_id = fields.Many2one('gescoth.eleve', string="Elève", required=True)
	classe_id = fields.Many2one('gescoth.classe', string="Classe", required=True)
	coeficient_id = fields.Many2one('gescoth.coeficient', string="Matière", required=True)
	saison = fields.Selection([
		('s1','Semestre 1 - Trimestre 1'),
		('s2','Semestre 2 - Trimestre 2'),
		('s3','Semestre 3 - Trimestre 3')
		], 
		required=True,
	)
	moy_classe = fields.Float(string="Séquence 1", store=True, group_operator='avg')
	s1_is_not_compose = fields.Boolean("N'a pas composé")
	rang_s1 = fields.Char(string="Rang", compute="CalculerRang_s1",)
	appreciation_s1 = fields.Char(string='Appréciation', compute='_appreciation_s1')

	note_compo = fields.Float(string="Séquence 2", store=True, group_operator='avg')
	s2_is_not_compose = fields.Boolean("N'a pas composé")
	rang_s2 = fields.Char(string="Rang", compute="CalculerRang_s2",)
	appreciation_s2 = fields.Char(string='Appréciation', compute='_appreciation_s2')

	moyenne = fields.Float(string="Moyenne", default=0, store=True, group_operator='avg')
	rang = fields.Char(string="Rang", compute="CalculerRang",)
	annee_scolaire = fields.Many2one('gescoth.anneescolaire', required=True, string="Année scolaire",)
	professeur_id = fields.Many2one('gescoth.professeur', "Professeur")
	appreciation = fields.Char(string='Appréciation', compute='Appreciation')
	
	state = fields.Selection([
		('0', 'Non validé'),
		('1', 'Validé'),
	], default="0", readonly=True)


	def write(self, values):
		res = super().write(values)
		note = self.env['gescoth.note.annuelle'].search([
			('eleve_id','=', self.eleve_id.id),
			('classe_id','=', self.classe_id.id),
			('coeficient_id','=', self.coeficient_id.id),
			('annee_scolaire','=', self.annee_scolaire.id),
		], limit=1)
		if note:
			vals = {}
			# raise ValidationError(_(self.saison))
			if self.saison == 's1':				
				if values.__contains__('moy_classe'):
					vals['note_sequence1'] = values['moy_classe']

				if values.__contains__('s1_is_not_compose'):
					vals['s1_is_not_compose'] = values['s1_is_not_compose']

				if values.__contains__('note_compo'):
					vals['note_sequence2'] = values['note_compo']

				if values.__contains__('s2_is_not_compose'):
					vals['s2_is_not_compose'] = values['s2_is_not_compose']

			if self.saison == 's2':
				if values.__contains__('moy_classe'):
					vals['note_sequence3'] = values['moy_classe']

				if values.__contains__('s1_is_not_compose'):
					vals['s3_is_not_compose'] = values['s1_is_not_compose']

				if values.__contains__('note_compo'):
					vals['note_sequence4'] = values['note_compo']

				if values.__contains__('s2_is_not_compose'):
					vals['s4_is_not_compose'] = values['s2_is_not_compose']

			if self.saison == 's3':
				if values.__contains__('moy_classe'):
					vals['note_sequence5'] = values['moy_classe']

				if values.__contains__('s1_is_not_compose'):
					vals['s5_is_not_compose'] = values['s1_is_not_compose']

				if values.__contains__('note_compo'):
					vals['note_sequence6'] = values['note_compo']

				if values.__contains__('s2_is_not_compose'):
					vals['s6_is_not_compose'] = values['s2_is_not_compose']

			note.write(vals)
		return res

	@api.model
	def create(self, values):
		result = super().create(values)
		note_annuelle = {
			'eleve_id': values['eleve_id'] , 
			'classe_id': values['classe_id'] , 
			'coeficient_id': values['coeficient_id'],
			'saison': values['saison'], 
			'annee_scolaire':values['annee_scolaire'],
		}
		note = self.env['gescoth.note.annuelle'].search([
			('eleve_id','=', values['eleve_id']),
			('classe_id','=', values['classe_id']),
			('coeficient_id','=', values['coeficient_id']),
			('annee_scolaire','=', values['annee_scolaire']),
		], limit=1)

		if not note:
			self.env['gescoth.note.annuelle'].create(note_annuelle)

		return result
	# @api.onchange('note_compo','moy_classe')
	def CalculerRang(self):
		for rec in self:
			data = list()
			notes = self.env['gescoth.note'].search([
				('classe_id','=', rec.classe_id.id),
				('saison','=', rec.saison),
				('coeficient_id','=', rec.coeficient_id.id),
			])
			for note in notes:
				data.append(note.moyenne)
			
			rec.rang = Rang(rec.moyenne, rec.eleve_id.sexe, data)

	def CalculerRang_s2(self):
		for rec in self:
			data = list()
			notes = self.env['gescoth.note'].search([
				('classe_id','=', rec.classe_id.id),
				('saison','=', rec.saison),
				('coeficient_id','=', rec.coeficient_id.id),
			])
			for note in notes:
				data.append(note.note_compo)
			
			rec.rang_s2 = Rang(rec.note_compo, rec.eleve_id.sexe, data)
	    
	def CalculerRang_s1(self):
		for rec in self:
			data = list()
			notes = self.env['gescoth.note'].search([
				('classe_id','=', rec.classe_id.id),
				('saison','=', rec.saison),
				('coeficient_id','=', rec.coeficient_id.id),
			])
			for note in notes:
				data.append(note.moy_classe)
			
			rec.rang_s1 = Rang(rec.moy_classe, rec.eleve_id.sexe, data)

	@api.onchange('moy_classe','note_compo')	    
	def Appreciation(self):
		appr = self.env['gescoth.appreciation'].search([])
		for rec in self:
			for ap in appr:
				if rec.moyenne >= ap.inf and rec.moyenne < ap.sup:
					rec.appreciation = ap.name
					return
				if rec.moyenne >= 20:
					rec.appreciation = 'Excellent'
				else:
					rec.appreciation = 'Excellent'

	@api.onchange('note_compo')	    
	def _appreciation_s2(self):
		appr = self.env['gescoth.appreciation'].search([])
		for rec in self:
			for ap in appr:
				if rec.note_compo >= ap.inf and rec.note_compo < ap.sup:
					rec.appreciation_s2 = ap.name
					return
				if rec.note_compo >= 20:
					rec.appreciation_s2 = 'Excellent'
				else:
					rec.appreciation_s2 = 'Excellent'


	@api.onchange('moy_classe')	    
	def _appreciation_s1(self):
		appr = self.env['gescoth.appreciation'].search([])
		for rec in self:
			for ap in appr:
				if rec.moy_classe >= ap.inf and rec.moy_classe < ap.sup:
					rec.appreciation_s1 = ap.name
					return
				if rec.moyenne >= 20:
					rec.appreciation_s1 = 'Excellent'
				else:
					rec.appreciation_s1 = 'Excellent'

	@api.constrains('moy_classe','note_compo','s1_is_not_compose','s2_is_not_compose')
	def check_notes(self):
		for rec in self:
			if rec.moy_classe < 0 or rec.moy_classe > 20:
				raise ValidationError(_('La moyenne de classe doit être entre 0 et 20. Vous avez taper : ' + str(rec.moy_classe)))
			if rec.note_compo < 0 or rec.note_compo> 20:
				raise ValidationError(_('La moyenne de classe doit être entre 0 et 20. Vous avez taper : ' + str(rec.note_compo)))

	@api.onchange('moy_classe','note_compo','s1_is_not_compose','s2_is_not_compose')
	def _onchange_note_compo(self):
		for rec in self:
			res = 0
			n = 0
			if not rec.s1_is_not_compose:
				res += rec.moy_classe
				n += 1
			if not rec.s2_is_not_compose:
				res += rec.note_compo
				n += 1
			if rec.coeficient_id.est_facultative:
				if res > 10:
					rec.moyenne = res-10
				else:
					rec.moyenne = 0
			else:
				if n != 0:
					rec.moyenne = res / n
				else:
					rec.moyenne = res




class GescothAppreciation(models.Model):
	_name = 'gescoth.appreciation'
	_description = 'Gestion des appications'

	name= fields.Char(string="Appréciation")
	inf = fields.Float(string='Inférieur')
	sup = fields.Float(string='Supérieur')

class GescothDecision(models.Model):
	_name = 'gescoth.decision'
	_description = 'Décision'

	name= fields.Char(string="Décision")
	inf = fields.Float(string='Inférieur')
	sup = fields.Float(string='Supérieur')

class GescothResultatExamen(models.Model):
    _name = 'gescoth.examen.resultat'
    _description = "Resultat de l'exament"
    _rec_name = 'eleve_id'

    eleve_id = fields.Many2one(
        'gescoth.eleve',
        string='Eleve',
        required=True,
    )
    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Classe',
        required=True,
    )

    saison = fields.Selection([
		('s1','Semestre 1 - Trimestre 1'),
		('s2','Semestre 2 - Trimestre 2'),
		('s3','Semestre 3 - Trimestre 3')
		], 
		required=True,
	)

    annee_scolaire = fields.Many2one(
    	'gescoth.anneescolaire', 
    	required=True, 
    	string="Année scolaire",
    )
    moyenne = fields.Float(
        string='Moyenne',
    )
    rang = fields.Char(
        string='Rang',
    )
    result = fields.Selection(string='Resultat', selection=[
		('0', 'Admis'),
		('1', 'Ajourné'),
	])

    state = fields.Selection([
		('0', 'Non validé'),
		('1', 'Validé'),
	], default="0")

class GescothResultatAnnuelExamen(models.Model):
    _name = 'gescoth.examen.annuel.resultat'
    _description = "Resultat annuel de l'exament"
    _rec_name = 'eleve_id'

    eleve_id = fields.Many2one(
        'gescoth.eleve',
        string='Eleve',
        required=True,
    )
    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Classe',
        required=True,
    )

    annee_scolaire = fields.Many2one(
    	'gescoth.anneescolaire', 
    	required=True, 
    	string="Année scolaire",
    )
    moyenne = fields.Float(
        string='Moyenne',
    )
    rang = fields.Char(
        string='Rang',
    )
    result = fields.Selection(string='Resultat', selection=[
		('0', 'Admis'),
		('1', 'Ajourné'),
	])

    nombre = fields.Float(string='Nombre de séquence')

    state = fields.Selection([
		('0', 'Non validé'),
		('1', 'Validé'),
	], default="0")


class GescothProgramExamen(models.Model):
    _name = 'gescoth.examen.program'
    _description = "Programme d'examen"

    name = fields.Char(
    	string='Description',
    )
    date_debut = fields.Date(
        string='Date de début'
    )

    date_fin = fields.Date(
        string='Date de fin'
    )
    annee_scolaire = fields.Many2one(
    	'gescoth.anneescolaire', 
    	required=True, 
    	string="Année scolaire",
    )

    organisateur = fields.Many2one(
    	'gescoth.personnel', 
    	required=True, 
    	string="Organisateur",
    )
    line_ids = fields.One2many(
        'gescoth.program.line',
        'program_id',
        string='Programmes',
    )

class GescothProgramLine(models.Model):
    _name = 'gescoth.program.line'
    _rec_name="classe_id"

    date_examen = fields.Date(
        string='Date',
    )
    heure_debut = fields.Float(
        string='Heure de début',
    )
    heure_fin = fields.Float(
        string='Heure de fin',
    )

    professeur_id = fields.Many2one(
        'gescoth.professeur',
        string='Prof Surveillant',
    )
    classe_id = fields.Many2one(
        'gescoth.classe',
        string='Classe',
    )
    matiere_id = fields.Many2one(
        'gescoth.matiere',
        string='Matière',
    )
    program_id = fields.Many2one(
        'gescoth.examen.program',
        string='Programme',
    )
class GescothExamenDeliberation(models.Model):

	_name = 'gescoth.examen.deliberation'
	_description = 'Délibération'

	classe_id = fields.Many2one(
		'gescoth.classe',
		string='Classe',
		)
	

