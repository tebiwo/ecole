# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from .. functions.myFunctions import *
from math import *


class GescothBulletinSequence(models.TransientModel):
	_name = 'gescoth.bulletin.sequence'
	_description = "Bulletin par séquence"

	classe_id = fields.Many2one('gescoth.classe', string='classe', required=True,)
	annee_scolaire_id = fields.Many2one(
		'gescoth.anneescolaire',
		required=True,
		string="Année scolaire",
		default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('gescoth.annee_scolaire_id')),
	)
	date_signature = fields.Date(
	    string='Date de signature',
	    required=True,
	    default=fields.date.today(),
	)
	eleve_id = fields.Many2one(
		'gescoth.eleve',
		string='Eleve',
		# domain=[('classe_id','=',self.classe_id.id), ],
		)
	saison = fields.Selection([
		('s1','Semestre 1 - Trimestre 1'),
		('s2','Semestre 2 - Trimestre 2'),
		('s3','Semestre 3 - Trimestre 3')
		], 
		required=True,
	)
	sequence = fields.Selection([
		('sq1','Séquence 1'),
		('sq2','Séquence 2'),
	    ], 
		required=True,
	)
	est_un_strimestre = fields.Boolean(string="Est un trimestre")
	type_de_saison = fields.Selection([
		('semestre', 'Semestre'),
		('trimestre', 'Trimestre')
	],required=True,)

	def imprimer_bulletin_sequence(self):
		data = {}
		liste_note = []
		liste_note_total_s1 = []
		liste_note_total_s2 = []
		liste_note_total = []
		eleve_ids = self.env['gescoth.eleve.inscription'].search([
			('classe_id','=', self.classe_id.id),
			('annee_scolaire_id','=', self.annee_scolaire_id.id)
		])
		if len(eleve_ids) <= 0:
			raise ValidationError(_("Pas encore d'élève dans cette classe !"))
		for el in eleve_ids:
			eleve = {
				'id':el.eleve_id.id,
				'nom_eleve': el.eleve_id.nom_eleve,
				'matricule':el.eleve_id.name,
				'date_naissance':el.eleve_id.date_naissance,
				'lieu_naissance':el.eleve_id.lieu_naissance,
				'classe':el.eleve_id.classe.name,
				'sexe':'Masculin' if el.eleve_id.sexe == 'masculin' else 'Féminin',
				'Apt_sport':el.eleve_id.Apt_sport,
				'statut':el.eleve_id.statut,
				'saison':'Premiere trimestre',
				'conduite':el.eleve_id.afficher_conduite(self.annee_scolaire_id.id,'s1'),
			}
			el_note_ids = self.env['gescoth.note'].search([('eleve_id','=', el.eleve_id.id),('saison','=','s1'),('annee_scolaire','=', self.annee_scolaire_id.id)])
			
			if len(el_note_ids) <= 0:
				raise ValidationError(_("Veuillez générer toutes les notes d'abord !"))
			note_eleve = []
			coef= 0
			total_s1 = 0
			total_s2 = 0
			total = 0
			for note in el_note_ids:
				matiere = note.coeficient_id.matiere.nom_abrege if note.coeficient_id.matiere.user_abrege else note.coeficient_id.matiere.name
				vals_note = {
					'matiere' : matiere,
					'groupe_id': note.coeficient_id.matiere.group_id.id,
					'type_matiere': note.coeficient_id.matiere.type_matiere,

					'sequence1':note.moy_classe,
					's1_est_compose':not note.s1_is_not_compose,
					'rang_s1':note.rang_s1,
					'appreciation_s1':note.appreciation_s1,
					'total_s1':note.moy_classe * note.coeficient_id.coef,

					'sequence2': note.note_compo,
					's2_est_compose':not note.s2_is_not_compose,
					'rang_s2':note.rang_s2,
					'appreciation_s2':note.appreciation_s2,
					'total_s2':note.note_compo * note.coeficient_id.coef,

					'moyenne':note.moyenne,
					'coef':note.coeficient_id.coef,
					'total': note.moyenne * note.coeficient_id.coef,
					'rang':note.rang,
					'appreciation':note.appreciation,
					'prof':note.coeficient_id.professeur_id.name,
					
				}
				if note.coeficient_id.matiere.type_matiere == 'sport' and not el.Apt_sport or note.s1_is_not_compose or note.s2_is_not_compose: 
					pass
				else:
					if not note.coeficient_id.est_facultative:
						coef += note.coeficient_id.coef
					total_s1 += (note.moy_classe * note.coeficient_id.coef)
					total_s2 += (note.note_compo * note.coeficient_id.coef)
					total += (note.moyenne * note.coeficient_id.coef)
				note_eleve.append(vals_note)

			eleve['total_coef'] = coef

			eleve['total_moyenne_s1'] = total_s1
			eleve['moyenne_sur_vingt_s1'] = round((total_s1/coef),2)
			# eleve['notes'] = note_eleve

			eleve['total_moyenne_s2'] = total_s2
			eleve['moyenne_sur_vingt_s2'] = round((total_s2/coef),2)
			# eleve['notes'] = note_eleve

			eleve['total_moyenne'] = total
			eleve['moyenne_sur_vingt'] = round((total/coef),2)
			
			eleve['notes'] = note_eleve
			
			liste_note.append(eleve)

			liste_note_total_s1.append(round((total_s1/coef),2))
			liste_note_total_s2.append(round((total_s2/coef),2))
			liste_note_total.append(round((total/coef),2))

		for el in liste_note:
			el['rang_s1'] = Rangb(el['moyenne_sur_vingt_s1'],el['sexe'],liste_note_total_s1)
			el['rang_s2'] = Rangb(el['moyenne_sur_vingt_s2'],el['sexe'],liste_note_total_s2)
			el['rang'] = Rangb(el['moyenne_sur_vingt'],el['sexe'],liste_note_total)


		if self.saison == 's1':
			liste_note = sorted(liste_note, key=lambda x: x['moyenne_sur_vingt_s1'], reverse=True)

		if self.saison == 's2':
			liste_note = sorted(liste_note, key=lambda x: x['moyenne_sur_vingt_s2'], reverse=True)


		#appréciations générales sequence 1
		decision = self.env['gescoth.decision'].search([])
		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Excellence":
					if el['moyenne_sur_vingt_s1'] >= dc.inf and el['moyenne_sur_vingt_s1'] < dc.sup:
						el['tableau_excellence_s1'] = "Oui"
					else:
						el['tableau_excellence_s1'] = ""

		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Honneur + Félicitations":
					if el['moyenne_sur_vingt_s1'] >= dc.inf and el['moyenne_sur_vingt_s1'] < dc.sup:
						el['tableau_honneur_felicitation_s1'] = "Oui"
					else:
						el['tableau_honneur_felicitation_s1'] = ""


		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Honneur + Encouragements":
					if el['moyenne_sur_vingt_s1'] >= dc.inf and el['moyenne_sur_vingt_s1'] < dc.sup:
						el['tableau_honneur_encouragement_s1'] = "Oui"
					else:
						el['tableau_honneur_encouragement_s1'] = ""


		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Honneur":
					if el['moyenne_sur_vingt_s1'] >= dc.inf and el['moyenne_sur_vingt_s1'] < dc.sup:
						el['tableau_honneur_s1'] = "Oui"
					else:
						el['tableau_honneur_s1'] = ""

		for el in liste_note:
			for dc in decision:
				if dc.name == "Avertissement":
					if el['moyenne_sur_vingt_s1'] >= dc.inf and el['moyenne_sur_vingt_s1'] < dc.sup:
						el['avertissement_s1'] = "Oui"
					else:
						el['avertissement_s1'] = ""

		for el in liste_note:
			for dc in decision:
				if dc.name == "Blâme":
					if el['moyenne_sur_vingt_s1'] >= dc.inf and el['moyenne_sur_vingt_s1'] < dc.sup:
						el['blame_s1'] = "Oui"
					else:
						el['blame_s1'] = ""

		#appréciations générales sequence 2
		decision = self.env['gescoth.decision'].search([])
		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Excellence":
					if el['moyenne_sur_vingt_s2'] >= dc.inf and el['moyenne_sur_vingt_s2'] < dc.sup:
						el['tableau_excellence_s2'] = "Oui"
					else:
						el['tableau_excellence_s2'] = ""

		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Honneur + Félicitations":
					if el['moyenne_sur_vingt_s2'] >= dc.inf and el['moyenne_sur_vingt_s2'] < dc.sup:
						el['tableau_honneur_felicitation_s2'] = "Oui"
					else:
						el['tableau_honneur_felicitation_s2'] = ""


		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Honneur + Encouragements":
					if el['moyenne_sur_vingt_s2'] >= dc.inf and el['moyenne_sur_vingt_s2'] < dc.sup:
						el['tableau_honneur_encouragement_s2'] = "Oui"
					else:
						el['tableau_honneur_encouragement_s2'] = ""


		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Honneur":
					if el['moyenne_sur_vingt_s2'] >= dc.inf and el['moyenne_sur_vingt_s2'] < dc.sup:
						el['tableau_honneur_s2'] = "Oui"
					else:
						el['tableau_honneur_s2'] = ""

		for el in liste_note:
			for dc in decision:
				if dc.name == "Avertissement":
					if el['moyenne_sur_vingt_s2'] >= dc.inf and el['moyenne_sur_vingt_s2'] < dc.sup:
						el['avertissement_s2'] = "Oui"
					else:
						el['avertissement_s2'] = ""

		for el in liste_note:
			for dc in decision:
				if dc.name == "Blâme":
					if el['moyenne_sur_vingt_s2'] >= dc.inf and el['moyenne_sur_vingt_s2'] < dc.sup:
						el['blame_s2'] = "Oui"
					else:
						el['blame_s2'] = ""

		#appréciations générales
		decision = self.env['gescoth.decision'].search([])
		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Excellence":
					if el['moyenne_sur_vingt'] >= dc.inf and el['moyenne_sur_vingt'] < dc.sup:
						el['tableau_excellence'] = "Oui"
					else:
						el['tableau_excellence'] = ""

		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Honneur + Félicitations":
					if el['moyenne_sur_vingt'] >= dc.inf and el['moyenne_sur_vingt'] < dc.sup:
						el['tableau_honneur_felicitation'] = "Oui"
					else:
						el['tableau_honneur_felicitation'] = ""


		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Honneur + Encouragements":
					if el['moyenne_sur_vingt'] >= dc.inf and el['moyenne_sur_vingt'] < dc.sup:
						el['tableau_honneur_encouragement'] = "Oui"
					else:
						el['tableau_honneur_encouragement'] = ""


		for el in liste_note:
			for dc in decision:
				if dc.name == "Tableau d'Honneur":
					if el['moyenne_sur_vingt'] >= dc.inf and el['moyenne_sur_vingt'] < dc.sup:
						el['tableau_honneur'] = "Oui"
					else:
						el['tableau_honneur'] = ""

		for el in liste_note:
			for dc in decision:
				if dc.name == "Avertissement":
					if el['moyenne_sur_vingt'] >= dc.inf and el['moyenne_sur_vingt'] < dc.sup:
						el['avertissement'] = "Oui"
					else:
						el['avertissement'] = ""

		for el in liste_note:
			for dc in decision:
				if dc.name == "Blâme":
					if el['moyenne_sur_vingt'] >= dc.inf and el['moyenne_sur_vingt'] < dc.sup:
						el['blame'] = "Oui"
					else:
						el['blame'] = ""


		ICPSudo = self.env['ir.config_parameter'].sudo()
		data['ville'] = ICPSudo.get_param('gescoth.ville')

		chef_id = self.env['ir.config_parameter'].sudo().get_param('gescoth.chef_etablissement')
		if int(chef_id) <= 0 or chef_id == None:
			raise ValidationError(_('Veuillez vérifier les parmatres du chef détablissement'))
		chef = self.env['gescoth.personnel'].search([('id','=', chef_id)])[0]

		liste_definitive = []
		list_unique = []

		for eleve in liste_note:
			if eleve['id'] == self.eleve_id.id:
				list_unique.append(eleve)
		if len(list_unique) == 1:
			liste_definitive = list_unique
		else :
			liste_definitive = liste_note

		groups = self.env['gescoth.matiere.groupe'].search([])
		groupe_matieres = []
		for group in groups:
			vals = {
				'id':group.id,
				'groupe_name':group.name,
			}
			groupe_matieres.append(vals)

		data['moyMaxi_s1'] = round(max(liste_note_total_s1),2)
		data['moyMini_s1'] = round(min(liste_note_total_s1),2)
		data['moyGene_s1'] = round(sum(liste_note_total_s1)/len(eleve_ids),2)

		data['moyMaxi_s2'] = round(max(liste_note_total_s2),2)
		data['moyMini_s2'] = round(min(liste_note_total_s2),2)
		data['moyGene_s2'] = round(sum(liste_note_total_s2)/len(eleve_ids),2)

		data['moyMaxi'] = round(max(liste_note_total),2)
		data['moyMini'] = round(min(liste_note_total),2)
		data['moyGene'] = round(sum(liste_note_total)/len(eleve_ids),2)

		data['note_des_eleve'] = liste_definitive
		data['anneescolaire_id'] = self.annee_scolaire_id.name
		data['effectif'] = len(eleve_ids)
		data['date_signature'] = self.date_signature.strftime('%d/%m/%Y')
		data['chef_etablissement'] = chef.name
		data['titre_chef_etablissement'] = chef.post_id.name
		data['prof'] = self.classe_id.professeur.name
		data['entete'] = self.env['ir.config_parameter'].sudo().get_param('gescoth.entete')
		data['saison'] = self.saison
		data['sequence']= self.sequence
		data['groupe_matieres'] = groupe_matieres

		semestres = {
			's1':'Premier semestre',
			's2':'Sencond semestre',
			's3':'Troisième semestre',
		}
		trimestres = {
			's1' :'Premier trimestre',
			's2' :'Sencond trimestre',
			's3' :'Troisième trimestre'
		}
		sequences ={
			'sq1':'Séquence 1',
			'sq2':'Séquence 2',
		}
		data['saison_name'] = trimestres[self.saison] if self.type_de_saison == 'trimestre' else semestres[self.saison]
		data['sequence_name']=sequences[self.sequence]
		data['est_un_strimestre'] = self.est_un_strimestre
		
		return self.env.ref('gescoth.bulletin_par_sequence_report_view').report_action(self, data=data)
