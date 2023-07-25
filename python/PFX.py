from CvPythonExtensions import *
import CvUtil
import CvScreensInterface
import CvDebugTools
import CvWBPopups
import PyHelpers
import Popup as PyPopup
import CvCameraControls
import CvTopCivs
import sys
import CvWorldBuilderScreen
import CvAdvisorUtils
import CvTechChooser
import pickle

import CvIntroMovieScreen
import CustomFunctions


# globals

cf = CustomFunctions.CustomFunctions()
gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
getInfoType = gc.getInfoTypeForString
getPlot	= CyMap().plot

getPlayer = gc.getPlayer

def GreatLeaderFollowerType(iPlayer):
	pPlayer = gc.getPlayer(iPlayer)
	infoCiv = gc.getCivilizationInfo(pPlayer.getCivilizationType())
		
	if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_MITHRIL_WORKING')) and not pPlayer.isUnitClassMaxedOut(getInfoType('UNITCLASS_PHALANX'),0):
		iUnit = infoCiv.getCivilizationUnits(getInfoType('UNITCLASS_PHALANX'))
		if iUnit == -1:
			iUnit = getInfoType('UNIT_PHALANX')
	elif pPlayer.isHasTech(gc.getInfoTypeForString('TECH_IRON_WORKING')):
		iUnit = infoCiv.getCivilizationUnits(getInfoType('UNITCLASS_CHAMPION'))
		if iUnit == -1:
			iUnit = getInfoType('UNIT_CHAMPION')
	elif pPlayer.isHasTech(gc.getInfoTypeForString('TECH_BRONZE_WORKING')):
		iUnit = infoCiv.getCivilizationUnits(getInfoType('UNITCLASS_AXEMAN'))
		if iUnit == -1:
			iUnit = getInfoType('UNIT_AXEMAN')
	else:
		iUnit = infoCiv.getCivilizationUnits(getInfoType('UNITCLASS_WARRIOR'))
		if iUnit == -1:
			iUnit = getInfoType('UNIT_WARRIOR')		

	return iUnit

def onCityAcquired(self, argsList): # triggered whenever a city is captured (before the player chooses to keep or raze)
	'City Acquired'
	iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
	gc 		= CyGlobalContext()
	cf		= self.cf
	game 		= CyGame()
	getPlayer 	= gc.getPlayer
	pPlayer 	= getPlayer(iNewOwner)
	hasTrait 	= pPlayer.hasTrait
	pPlot 		= pCity.plot()
	setBuilding = pCity.setNumRealBuilding
	changePop	= pCity.changePopulation
	iCiv		= pPlayer.getCivilizationType()
	iCityOwner 	= pCity.getOwner()
	pCityOwner	= getPlayer(iCityOwner)
	Civ	 	= self.Civilizations
	Trait 		= self.Traits
	Leader 		= self.Leaders
	Civic 		= self.Civics
	Rel	 	= self.Religions
	Building 	= self.Buildings
	Unit		= self.Units
	iPop		= pCity.getPopulation()
	pPrevious	= getPlayer(iPreviousOwner)
	iNoAI 		= UnitAITypes.NO_UNITAI
	iSouth		= DirectionTypes.DIRECTION_SOUTH
	iPrevCiv = pPrevious.getCivilizationType()
	
	if bConquest and pPlayer.hasTrait(getInfoType('TRAIT_DIVINER')):
		iFollower = GreatLeaderFollowerType(iNewOwner)
		if iFollower != -1:
			newUnit = pPlayer.initUnit(iFollower, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			CyInterface().addMessage(iNewOwner,true,25,"A soldier joins your cause!",'',0,'',ColorTypes(11), pCity.getX(), pCity.getY(), True,True)
			
	if pPrevious.getNumCities() == 0:
		if pPlayer.hasTrait(getInfoType('TRAIT_USURPER')):
			for iTrait in range(gc.getNumTraitInfos()):
				if pPrevious.hasTrait(iTrait) and (gc.getTraitInfo(iTrait).isSelectable()) and not pPlayer.hasTrait(iTrait):
					if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
						pPlayer.setHasTrait(iTrait,True,-1,True,True)
                        
		if pPlayer.hasTrait(getInfoType('TRAIT_ABIDER')):
			for pLoopUnit in PyPlayer(iNewOwner).getUnitList():
				pLoopUnit.changeFreePromotionPick(1)
					
		if pPlayer.hasTrait(getInfoType('TRAIT_EXONERATOR')):
			for pLoopUnit in PyPlayer(iPreviousOwner).getUnitList():
				newUnit = pPlayer.initUnit(pLoopUnit.getUnitType(), pLoopUnit.getX(), pLoopUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                newUnit.convert(pLoopUnit)    
					
def onUnitCreated(self, argsList):
	'Unit Completed'
	pUnit              = argsList[0]
	self.verifyLoaded()
	gc                 = CyGlobalContext()
	cf                 = self.cf
	game               = CyGame()
	player             = PyPlayer(pUnit.getOwner())
	getPlayer          = gc.getPlayer
	pPlayer            = getPlayer(pUnit.getOwner())
	Civ                = self.Civilizations
	Promo              = self.Promotions["Effects"]
	Generic            = self.Promotions["Generic"]
	Race               = self.Promotions["Race"]
	Equipment          = self.Promotions["Equipment"]
	UnitCombat         = self.UnitCombats
	Tech               = self.Techs
	Mana               = self.Mana
	Civic	           = self.Civics
	setPromo           = pUnit.setHasPromotion
	hasTrait           = pPlayer.hasTrait
	Trait              = self.Traits
	iUnitType          = pUnit.getUnitType()
	initUnit           = pPlayer.initUnit
	getNumAvailBonuses = pPlayer.getNumAvailableBonuses
	getTeam            = gc.getTeam
	hasPromo           = pUnit.isHasPromotion
	randNum            = game.getSorenRandNum
	iNoAI              = UnitAITypes.NO_UNITAI
	iSouth             = DirectionTypes.DIRECTION_SOUTH
	pPlot              = pUnit.plot()
	iX                 = pPlot.getX(); iY = pPlot.getY()
	setName            = pUnit.setName
	iCiv		   = pPlayer.getCivilizationType()
	UnitClass	   = pUnit.getUnitClassType()
	UnitClassInfo	   = gc.getUnitClassInfo(pUnit.getUnitClassType())
	CombatList  = [getInfoType('UNITCOMBAT_ADEPT'),getInfoType('UNITCOMBAT_ARCHER'),getInfoType('UNITCOMBAT_DISCIPLE'),getInfoType('UNITCOMBAT_MELEE'),getInfoType('UNITCOMBAT_MOUNTED'),getInfoType('UNITCOMBAT_RECON')]
	RaceList = ['PROMOTION_POISON_RESISTANCE','PROMOTION_ORC','PROMOTION_LIZARDMAN_CUALLI','PROMOTION_WINTERBORN','PROMOTION_DWARF','PROMOTION_ELF','PROMOTION_LIZARDMAN_MAZATL','PROMOTION_SHADE','PROMOTION_DARK_ELF']
	
	if gc.getInfoTypeForString('PROMOTION_ALFAR') != -1:
		RaceList.append('PROMOTION_ALFAR')
    
 	if pPlayer.hasTrait(getInfoType('TRAIT_GRAND_MARSHAL')) and pUnit.getUnitCombatType() in CombatList and not pUnit.isHasPromotion(getInfoType('PROMOTION_CORPORAL')):
		pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_CORPORAL'),True)
                
	if pPlayer.hasTrait(getInfoType('TRAIT_DIVERSE')) and pUnit.getRace() == -1 and pUnit.isAlive() and not (UnitClassInfo.isUnique() or isWorldUnitClass(UnitClass)):
		iChance = 20 
		if CyGame().getSorenRandNum(100, "Bob") <= iChance: 
			race = CyGame().getSorenRandNum(len(RaceList), "Bob")
			if 0 <= race < len(RaceList):
				race_name = RaceList[race]
				pUnit.setHasPromotion(gc.getInfoTypeForString(race_name), True)

def onUnitPromoted(self, argsList):
	'Unit Promoted'
	pUnit, iPromotion = argsList
	#player 	= PyPlayer(pUnit.getOwner())
	pPlayer		= getPlayer(pUnit.getOwner())
	hasPromo 	= pUnit.isHasPromotion
	iUnitType 	= pUnit.getUnitType()
	Promo		= self.Promotions["Effects"]
	Race		= self.Promotions["Race"]
	Generic		= self.Promotions["Generic"]
	UnitAI		= self.UnitAI
	CombatList  = [getInfoType('UNITCOMBAT_ADEPT'),getInfoType('UNITCOMBAT_ARCHER'),getInfoType('UNITCOMBAT_DISCIPLE'),getInfoType('UNITCOMBAT_MELEE'),getInfoType('UNITCOMBAT_MOUNTED'),getInfoType('UNITCOMBAT_RECON')]
	PromotList  = ['PROMOTION_SEARGENT','PROMOTION_MASTER_SEARGENT','PROMOTION_CAPTAIN','PROMOTION_GENERAL']
	
	if pPlayer.hasTrait(getInfoType('TRAIT_GRAND_MARSHAL')) and pUnit.getUnitCombatType() in CombatList:
		for iPromo in PromotList:
			if pUnit.getLevel() >= gc.getPromotionInfo(getInfoType(iPromo)).getMinLevel() and not pUnit.isHasPromotion(getInfoType(iPromo)):
				pUnit.setHasPromotion(gc.getInfoTypeForString(iPromo),True)
				
	if pPlayer.hasTrait(getInfoType('TRAIT_STRATEGIST3')):
		iChance = pUnit.getLevel() * 10
		if CyGame().getSorenRandNum(100, "Bob") <= iChance:
			if not pUnit.isHasPromotion(getInfoType('PROMOTION_HERO')):
				pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HERO'),True)
			pUnit.changeFreePromotionPick(1)
		
def onCityBuilt(self, argsList):
	'City Built'
	pCity 		= argsList[0]
	gc 		= CyGlobalContext()
	iOwner		= pCity.getOwner()
	pPlayer		= gc.getPlayer(iOwner)
	Civ		= self.Civilizations
	eCiv 		= pPlayer.getCivilizationType()
	Building	= self.Buildings
	setNumB		= pCity.setNumRealBuilding

	if pPlayer.hasTrait(getInfoType('TRAIT_GRAND_MARSHAL')) and pPlayer.getNumCities() == 1:
		infoCiv = gc.getCivilizationInfo(eCiv)
		iUnit = infoCiv.getCivilizationUnits(getInfoType('UNITCLASS_COMMANDER'))
		if iUnit == -1:
			iUnit = getInfoType('UNIT_COMMANDER')
		if pPlayer.getLeaderType() == getInfoType("LEADER_DECIUS"):
			iUnit = getInfoType('UNIT_DECIUS')
		pTomb = pPlayer.getCapitalCity()
		newUnit = pPlayer.initUnit(iUnit, pTomb.getX(), pTomb.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
        
def onBeginPlayerTurn(self, argsList):
	'Called at the beginning of a players turn'
	iGameTurn, iPlayer = argsList
	gc 				= CyGlobalContext()
	cf				= self.cf
	game 			= CyGame()
	getPlayer 		= gc.getPlayer
	iDemonTeam 		= gc.getDEMON_TEAM()
	pPlayer 		= getPlayer(iPlayer)
	bAI		 		= self.Tools.isAI(iPlayer)
	hasTrait 		= pPlayer.hasTrait
	isCivic 		= pPlayer.isCivic
	randNum 		= game.getSorenRandNum

	eCiv 			= pPlayer.getCivilizationType()
	eSpeed 			= game.getGameSpeedType()
	Civ				= self.Civilizations
	Civic			= self.Civics
	Trait			= self.Traits
	Speed			= self.GameSpeeds
	Status			= self.LeaderStatus
	#Event			= self.EventTriggers
	Define			= self.Defines
	trigger			= pPlayer.trigger
	triggerData		        = pPlayer.initTriggeredData
	Leader                  = pPlayer.getLeaderType()
    
	TraitList = ['TRAIT_USURPER', 'TRAIT_ABIDER', 'TRAIT_EXONERATOR']
	
	is_decius = 0
	
	for iTrait in TraitList:
		if pPlayer.hasTrait(getInfoType(iTrait)):
			pPlayer.setHasTrait(getInfoType(iTrait),False,-1,True,True)
			is_decius = 1
			
	if is_decius == 1:
		if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
			pPlayer.setHasTrait(getInfoType('TRAIT_USURPER'),True,-1,True,True)
		elif pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_GOOD'):
			pPlayer.setHasTrait(getInfoType('TRAIT_EXONERATOR'),True,-1,True,True)
		else:
			pPlayer.setHasTrait(getInfoType('TRAIT_ABIDER'),True,-1,True,True)
        
