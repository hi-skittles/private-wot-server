# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/physics_shared.py
# Compiled at: 2014-11-10 12:09:27
import BigWorld
import Math
import math
import material_kinds
from math import pi
from constants import IS_CLIENT
from debug_utils import *
G = 9.81
COHESION = 1.3
CONTACT_COHESION = 0.9
GRAVITY_FACTOR = 1.25
WEIGHT_SCALE = 0.001
GRAVITY_FACTOR_SCALED = GRAVITY_FACTOR * WEIGHT_SCALE
FORWARD_FRICTION = 0.07
MIN_SIDE_FRICTION = 0.6
MIN_SIDE_FRICTION_SPEED = 4.2
MAX_SIDE_FRICTION = 0.6
MAX_SIDE_FRICTION_SPEED = 11.1
CONTACT_NORMAL_SIDE_FRICTION = CONTACT_COHESION * 1.1
SIDE_FRICTION_SPEED_FACTOR = 0.5
BEG_SLIP_POWER = 1.0
END_SLIP_POWER = -1.0
BEG_SLIP_SPEED = 0.0
END_SLIP_SPEED = 2.0
MIN_SLIP_FRICTION = 0.0
MAX_SLIP_FRICTION = 6.0
MAX_SLIP_FRICTION_Y = 0.883
FWD_CONTACT_SLIP_FRICTION_FACTOR = 0.5
FWD_CONTACT_SLIP_FRICTION_POW = 1
FWD_CONTACT_SLIP_FRICTION_MAX = 2.0
FWD_SLIP_FRICTION_FACTOR = 0.035
FWD_SLIP_FRICTION_POW = 1
FWD_SLIP_FRICTION_MAX = 0.5
CONTINUUM_RESIST_SPEED = 1.0
CONTINUUM_RESIST = 1.0
SUSP_WEIGHT = 0.63
MIN_SPEED_AFFECT_ROT = 11.1
MAX_SPEED_AFFECT_ROT = 22.2
SPEED_AFFECT_ROT_DECREASE = 0.0
ROTATION_POWER_FRACTION = 0.85
BKWD_POWER_FRACTION = 1.0
ANG_ACCELERATION_TIME = 0.05
ROTATION_POWER_FACTOR = 1.0
ROLL_TRACTION = 5.76
ROLL_TRACTION_MIN = 0.0
ROLL_TRACTION_MAX = 0.35
BROKEN_TRACK_SIDE_FRICTION = 3.5 / COHESION
BROKEN_TRACK_FWD_FRICTION = 3.5 / COHESION
BROKEN_TRACK_ROT_FRICTION_MP = 0.7
BROKEN_TRACK_Y = 0.866
RISE_FRICTION_Y = 0.906
RISE_FRICTION = 50.0
SUSP_COMPRESSION_MIN = 0.85
SUSP_COMPRESSION_MIN_MASS = 60.0
SUSP_COMPRESSION_MAX = 0.88
SUSP_COMPRESSION_MAX_MASS = 30.0
SUSP_HARD_RATIO = 0.55
SUSP_INDENT = 0.2
SUSP_CLIMB_FRICTION = 0.8
SUSP_DAMP_MASS_MIN = 45.0
SUSP_DAMP_MASS_MAX = 90.0
SUSP_DAMP_MIN = 0.02
SUSP_DAMP_MAX = 0.03
COLLBOX_2_EXPAND = 0.93
BODY_HEIGHT = 1.4
CENTER_OF_MASS_Y = -0.8
TRACK_RESTITUTION = 0.3
FWD_FRICTION_Y = 1.41
LIFT_SPRING_STIFFNESS = 1.5
LIFT_SPRING_SIZE = 0.5
SUSP_SOFT_FRICTION = 0.2
TRACK_FWD_FRICTION = 0.0
TRACK_SIDE_FRICTION = 0.0
SUSP_SLUMP_FRICTION = 3.0
SUSP_SLUMP_FRICTION_BOUND = 0.0
FORCE_POINT_X = 0.5
FORCE_POINT_Y = 0.0
ROLLER_MODE = False if IS_CLIENT else True
COH_DECAY_COMPENSATION = 0.5
COH_DECAY_COMPENSATION_Y = 0.94
SLOPE_COH_DECAY_Y = 0.72
SLOPE_COH_DECAY = 0.25
_COH_DECAY_Y = 0.969
_COH_DECAY_FACTOR = 5.78
_COH_DECAY_POW = 3.0
_COH_DECAY_BOUND = 0.5
_STRAFE_THRESHOLD = 0.005
_SIMULATION_Y_BOUND = 1000.0
FREEZE_ANG_ACCEL_EPSILON = 0.05
FREEZE_ACCEL_EPSILON = 0.05
FREEZE_VEL_EPSILON = 0.05
FREEZE_ANG_VEL_EPSILON = 0.05
WIDTH_LONG = 6.2
WIDTH_VERY_LONG = 7.0
CLEARANCE_RATIO_LONG = 5.0
NUM_SPRINGS_LONG = 5
NUM_SPRINGS_NORMAL = 5
CENTER_ROTATION_SPEED = 5.5
CMY_MIN = -0.15
CMY_MID = -0.2
CMY_MAX = -0.3
SUSP_WEIGHT_MIN = 0.2
SUSP_WEIGHT_MID = 0.3
SUSP_WEIGHT_MAX = 0.4
DYN_RATIO_MIN = 9.5
DYN_RATIO_MID = 13.0
DYN_RATIO_MAX = 21.0
CLEARANCE = 1.75
CLEARANCE_MIN = 0.55
CLEARANCE_MAX = 0.6
VEHICLE_ON_OBSTACLE_COLLISION_BOX_MIN_HEIGHT = 1.1
STIFF_MP = 1.0
TRACK_LENGTH_FACTOR = 0.9
TRACK_LENGTH_MIN = 0.6
TRACK_LENGTH_MAX = 0.64
CLEARANCE_TO_LENGTH_MIN2 = 0.08
CLEARANCE_TO_LENGTH_MAX2 = 0.1
XI = 1.0
ZI = 1.0
HARD_RATIO_MIN = 0.5
CLEARANCE_TO_LENGTH_MIN = 0.085
HARD_RATIO_MAX = 0.52
CLEARANCE_TO_LENGTH_MAX = 0.112
_LOG_INIT_PARAMS = False
RESTITUTION = 0.5
FRICTION_RATIO = 1.0
NUM_ITERATIONS = 10
NUM_ITERATIONS_ACCURATE = 40
MID_SOLVING_ITERATIONS = 4
NUM_SUBSTEPS = 2
USE_SSE_SOLVER = True
WARMSTARTING_VEHICLE_VEHICLE = False
WARMSTARTING_VEHICLE_STATICS = False
WARMSTARTING_THRESHOLD = 0.1
USE_PSEUDO_CONTACTS = True
ALLOWED_PENETRATION = 0.01
CONTACT_PENETRATION = 0.1
TRACKS_PENETRATION = 0.01
IMPROVE_ACCURACY_MASS_RATIO = 10.0
CONTACT_ENERGY_POW = 3.0
CONTACT_ENERGY_POW2 = 0.75
ROLLER_RISE_STRONG_FRICTION = 4.0
SLOPE_FRICTION_FUNC_DEF = tuple((math.pi * ang / 180.0 for ang in (34.0, 50.0, 70.0)))
SLOPE_FRICTION_FUNC_VAL = (0.4, 2.0, 5.0)
SLOPE_FRICTION_MODELS_FUNC_VAL = (0.4, 0.45, 0.5)
CONTACT_FRICTION_TERRAIN = 1.0
CONTACT_FRICTION_STATICS = 0.25
CONTACT_FRICTION_STATICS_VERT = 3.0
CONTACT_FRICTION_DESTRUCTIBLES = 1.0
CONTACT_FRICTION_VEHICLES = 0.3
OVERTURN_CONSTR_MIN = 0.5
OVERTURN_CONSTR_MAX = 0.707
OVERTURN_CONSTR_ACCURATE = 0.866
OVERTURN_CONSTR_MARGIN = math.pi / 6.0
SINGLE_TRACK_POWER_FACTOR = 0.1
SINGLE_TRACK_Y = 0.866
SPEED_TO_CHANGE_ROTATION_DIR = 5.0
ARENA_BOUNDS_FRICTION_HOR = 0.2
ARENA_BOUNDS_FRICTION_VERT = 1.0
CLIMB_FRICTION_BOUND = 0.5
CLIMB_FRICTION_BIAS = 0.012 * SUSP_CLIMB_FRICTION
CLIMB_POWER_DECREASE = 0.4
_TRACK_RESTITUTION = 0.4
SUSP_USE_PSEUDO_SLIDER = True
SUSP_SLIDER_EXTENSION = 0.0
BOUNCE_Y = 0.707
CLIMB_TANG = 1.0
STAB_DAMP_MP = 5.0
STAB_EPSILON_AMBIT = 2.0
STAB_EPSILON_PERIOD = 4.0
g_confUpdaters = []

def init():
    updateCommonConf()


def updateCommonConf():
    BigWorld.wg_setupPhysicsParam('CONTACT_ENERGY_POW', CONTACT_ENERGY_POW)
    BigWorld.wg_setupPhysicsParam('CONTACT_ENERGY_POW2', CONTACT_ENERGY_POW2)
    BigWorld.wg_setupPhysicsParam('ROLLER_RISE_STRONG_FRICTION', ROLLER_RISE_STRONG_FRICTION)
    BigWorld.wg_setupPhysicsParam('SLOPE_FRICTION_FUNC_DEF', SLOPE_FRICTION_FUNC_DEF)
    BigWorld.wg_setupPhysicsParam('SLOPE_FRICTION_FUNC_VAL', SLOPE_FRICTION_FUNC_VAL)
    BigWorld.wg_setupPhysicsParam('SLOPE_FRICTION_MODELS_FUNC_VAL', SLOPE_FRICTION_MODELS_FUNC_VAL)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_TERRAIN', CONTACT_FRICTION_TERRAIN)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_STATICS', CONTACT_FRICTION_STATICS)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_STATICS_VERT', CONTACT_FRICTION_STATICS_VERT)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_DESTRUCTIBLES', CONTACT_FRICTION_DESTRUCTIBLES)
    BigWorld.wg_setupPhysicsParam('CONTACT_FRICTION_VEHICLES', CONTACT_FRICTION_VEHICLES)
    BigWorld.wg_setupPhysicsParam('OVERTURN_CONSTR_MIN', OVERTURN_CONSTR_MIN)
    BigWorld.wg_setupPhysicsParam('OVERTURN_CONSTR_MAX', OVERTURN_CONSTR_MAX)
    BigWorld.wg_setupPhysicsParam('OVERTURN_CONSTR_ACCURATE', OVERTURN_CONSTR_ACCURATE)
    BigWorld.wg_setupPhysicsParam('OVERTURN_CONSTR_MARGIN', OVERTURN_CONSTR_MARGIN)
    BigWorld.wg_setupPhysicsParam('SINGLE_TRACK_POWER_FACTOR', SINGLE_TRACK_POWER_FACTOR)
    BigWorld.wg_setupPhysicsParam('SINGLE_TRACK_Y', SINGLE_TRACK_Y)
    BigWorld.wg_setupPhysicsParam('SPEED_TO_CHANGE_ROTATION_DIR', SPEED_TO_CHANGE_ROTATION_DIR)
    BigWorld.wg_setupPhysicsParam('ARENA_BOUNDS_FRICTION_HOR', ARENA_BOUNDS_FRICTION_HOR)
    BigWorld.wg_setupPhysicsParam('ARENA_BOUNDS_FRICTION_VERT', ARENA_BOUNDS_FRICTION_VERT)
    BigWorld.wg_setupPhysicsParam('CLIMB_FRICTION_BOUND', CLIMB_FRICTION_BOUND)
    BigWorld.wg_setupPhysicsParam('CLIMB_FRICTION_BIAS', CLIMB_FRICTION_BIAS)
    BigWorld.wg_setupPhysicsParam('CLIMB_POWER_DECREASE', CLIMB_POWER_DECREASE)
    BigWorld.wg_setupPhysicsParam('TRACK_RESTITUTION', _TRACK_RESTITUTION)
    BigWorld.wg_setupPhysicsParam('SUSP_USE_PSEUDO_SLIDER', SUSP_USE_PSEUDO_SLIDER)
    BigWorld.wg_setupPhysicsParam('USE_PSEUDO_CONTACTS', USE_PSEUDO_CONTACTS)
    BigWorld.wg_setupPhysicsParam('CONTACT_PENETRATION', CONTACT_PENETRATION)
    BigWorld.wg_setupPhysicsParam('SUSP_SLIDER_EXTENSION', SUSP_SLIDER_EXTENSION)
    BigWorld.wg_setupPhysicsParam('WARMSTARTING_VEHICLE_VEHICLE', WARMSTARTING_VEHICLE_VEHICLE)
    BigWorld.wg_setupPhysicsParam('WARMSTARTING_VEHICLE_STATICS', WARMSTARTING_VEHICLE_STATICS)
    BigWorld.wg_setupPhysicsParam('WARMSTARTING_THRESHOLD', WARMSTARTING_THRESHOLD)
    BigWorld.wg_setupPhysicsParam('GRAVITY_COMPENSATION', (GRAVITY_FACTOR - 1.0) / GRAVITY_FACTOR)
    BigWorld.wg_setupPhysicsParam('BOUNCE_Y', BOUNCE_Y)
    BigWorld.wg_setupPhysicsParam('BROKEN_TRACK_Y', BROKEN_TRACK_Y)
    BigWorld.wg_setupPhysicsParam('CLIMB_TANG', CLIMB_TANG)
    BigWorld.wg_setupPhysicsParam('STAB_DAMP_MP', STAB_DAMP_MP)
    BigWorld.wg_setupPhysicsParam('STAB_EPSILON_AMBIT', STAB_EPSILON_AMBIT)
    BigWorld.wg_setupPhysicsParam('STAB_EPSILON_PERIOD', STAB_EPSILON_PERIOD)
    BigWorld.wg_setupPhysicsParam('IMPROVE_ACCURACY_MASS_RATIO', IMPROVE_ACCURACY_MASS_RATIO)
    strenghtMap = {'firm': 1,
     'medium': 2,
     'soft': 3}
    strenghtsByMatkinds = tuple(((matKind, strenghtMap[strStrenght]) for matKind, strStrenght in material_kinds.GROUND_STRENGTHS_BY_IDS.iteritems()))
    BigWorld.wg_setupGroundStrengths(strenghtsByMatkinds)


def updateConf():
    for e in BigWorld.entities.values():
        if e.className == 'Vehicle':
            initVehiclePhysics(e.mover.physics, e.typeDescriptor)

    updateCommonConf()
    for updater in g_confUpdaters:
        updater()


def computeRotationalCohesion(rotSpeedLimit, mass, length, width, enginePower):
    mg = mass * GRAVITY_FACTOR * G
    inertia = (width * width + length * length) * mass / 12.0
    return (rotSpeedLimit * inertia / ANG_ACCELERATION_TIME + enginePower / rotSpeedLimit) / mg


def initVehiclePhysics(physics, typeDesc):
    physDescr = typeDesc.physics
    hullMin, hullMax, _ = typeDesc.hull['hitTester'].bbox
    hullCenter = (hullMin + hullMax) * 0.5
    hullY = hullCenter.y + typeDesc.chassis['hullPosition'].y
    hullHeight = hullMax.y - hullMin.y
    bmin, bmax, _ = typeDesc.chassis['hitTester'].bbox
    chassisCenter = (bmin + bmax) * 0.5
    blen = bmax[2] - bmin[2]
    width = bmax[0] - bmin[0]
    height = bmax[1] - bmin[1]
    fullMass = physDescr['weight'] * WEIGHT_SCALE
    srcEnginePower = physDescr['enginePower']
    srcMass = physDescr['weight']
    suspMass = _computeSuspWeightRatio(srcMass, srcEnginePower) * fullMass
    if IS_CLIENT:
        hullMass = fullMass
    else:
        hullMass = fullMass - suspMass
    g = G * GRAVITY_FACTOR
    clearance = (typeDesc.chassis['hullPosition'].y + hullMin.y) * CLEARANCE
    clearance = _clamp(CLEARANCE_MIN * height, clearance, CLEARANCE_MAX * height)
    suspCompression = _computeSuspCompression(fullMass)
    if not IS_CLIENT:
        carringSpringLength = (clearance + TRACKS_PENETRATION) / suspCompression
    else:
        carringSpringLength = clearance / suspCompression
    hmg = hullMass * g
    cmShift = _computeCenterOfMassShift(srcMass, srcEnginePower)
    physics.centerOfMass = Math.Vector3((0.0, hullY + cmShift * hullHeight, 0.0))
    forcePtX = FORCE_POINT_X
    if IS_CLIENT:
        forcePtY = 0.0
    else:
        forcePtY = -physics.centerOfMass.y * suspMass / fullMass
        forcePtY = forcePtY + FORCE_POINT_Y * (-physics.centerOfMass.y - forcePtY)
    hullUpperBound = typeDesc.chassis['hullPosition'].y + hullMax.y
    chassisMaxY = bmax[1]
    hullPosY = typeDesc.chassis['hullPosition'][1]
    hullMaxY = hullPosY + hullMax[1]
    turretPosY = typeDesc.hull['turretPositions'][0][1]
    turretMaxY = hullPosY + turretPosY + typeDesc.turret['hitTester'].bbox[1][1]
    commonBoxMaxY = max(chassisMaxY, hullMaxY, turretMaxY)
    gunPosY = hullPosY + turretPosY + typeDesc.turret['gunPosition'][1]
    boxHeight = min(commonBoxMaxY, gunPosY, hullUpperBound * BODY_HEIGHT) - clearance
    boxHeight = max(chassisMaxY * 0.7, boxHeight, VEHICLE_ON_OBSTACLE_COLLISION_BOX_MIN_HEIGHT)
    globalBoxY = clearance + boxHeight / 2
    boxCenter = Math.Vector3(chassisCenter)
    boxCenter[1] = globalBoxY - physics.centerOfMass.y
    imp = hullMass / 12.0
    inertia = Math.Vector3((XI * imp * (height * height + blen * blen), imp * (width * width + blen * blen), ZI * imp * (width * width + height * height)))
    boxSize = Math.Vector3((width, boxHeight, blen))
    hardRatio = _computeHardRatio(clearance, blen)
    boxSize2 = Math.Vector3(boxSize)
    boxSize2.y = hullUpperBound
    globalBox2Y = boxSize2.y / 2
    boxCenter2 = Math.Vector3(chassisCenter)
    boxCenter2[1] = globalBox2Y - physics.centerOfMass.y
    physics.setupBody(boxSize, boxCenter, boxSize2, boxCenter2, hullMass, inertia)
    fwdSpeedLimit, bkwdSpeedLimit = physDescr['speedLimits']
    physics.fwdSpeedLimit = fwdSpeedLimit
    physics.bkwdSpeedLimit = bkwdSpeedLimit
    physics.brakeFriction = COHESION
    physics.forwardFriction = FORWARD_FRICTION
    physics.sideFrictionX = forcePtX * width
    physics.sideFrictionYMin = -forcePtY + ROLL_TRACTION_MIN * physics.centerOfMass.y
    physics.sideFrictionYMax = physics.sideFrictionYMin
    physics.sideFrictionYSpeed = ROLL_TRACTION * abs(physics.sideFrictionYMax - physics.sideFrictionYMin)
    physics.leftForcePt = Math.Vector3((-forcePtX * width, forcePtY, 0.0))
    physics.rightForcePt = Math.Vector3((forcePtX * width, forcePtY, 0.0))
    physics.centerRotationSpeed = CENTER_ROTATION_SPEED
    physics.rotationIsAroundCenter = physDescr['rotationIsAroundCenter']
    wlim = physDescr['rotationSpeedLimit']
    physics.enginePower = physDescr['enginePower'] * GRAVITY_FACTOR_SCALED
    if not IS_CLIENT:
        physics.slopeCohDecay = min(COHESION - _COH_DECAY_BOUND, SLOPE_COH_DECAY)
        physics.slopeCohDecayY = SLOPE_COH_DECAY_Y
        physics.compensateFrictionDecayRatio = COH_DECAY_COMPENSATION
        physics.compensateFrictionDecayY = COH_DECAY_COMPENSATION_Y
        physics.contactCohesion = CONTACT_COHESION
    physics.normalEnginePower = physics.enginePower
    physics.rotationSpeedLimit = wlim * physDescr['terrainResistance'][0]
    physics.trackCenterOffset = physDescr['trackCenterOffset']
    physics.rotationPowerFactor = ROTATION_POWER_FACTOR
    physics.minSideFriction = MIN_SIDE_FRICTION
    physics.minSideFrictionSpeed = MIN_SIDE_FRICTION_SPEED
    physics.maxSideFriction = MAX_SIDE_FRICTION
    physics.maxSideFrictionSpeed = MAX_SIDE_FRICTION_SPEED
    physics.sideFrictionSpeedK1 = SIDE_FRICTION_SPEED_FACTOR
    physics.contactNormalSideFriction = CONTACT_NORMAL_SIDE_FRICTION
    physics.begSlipFrictionPower = BEG_SLIP_POWER
    physics.endSlipFrictionPower = END_SLIP_POWER
    physics.begSlipFrictionSpeed = BEG_SLIP_SPEED
    physics.endSlipFrictionSpeed = END_SLIP_SPEED
    physics.minSlipFriction = MIN_SLIP_FRICTION
    physics.maxSlipFriction = MAX_SLIP_FRICTION
    physics.fwdContactSlipFrictionFactor = FWD_CONTACT_SLIP_FRICTION_FACTOR
    physics.fwdContactSlipFrictionPow = FWD_CONTACT_SLIP_FRICTION_POW
    physics.fwdContactSlipFrictionMax = FWD_CONTACT_SLIP_FRICTION_MAX
    physics.fwdSlipFrictionFactor = FWD_SLIP_FRICTION_FACTOR
    physics.fwdSlipFrictionPow = FWD_SLIP_FRICTION_POW
    physics.fwdSlipFrictionMax = FWD_SLIP_FRICTION_MAX
    physics.brokenTrackSideFriction = BROKEN_TRACK_SIDE_FRICTION
    physics.brokenTrackFwdFriction = BROKEN_TRACK_FWD_FRICTION
    physics.brokenTrackRotFrictionMP = BROKEN_TRACK_ROT_FRICTION_MP
    physics.rotationPowerFraction = ROTATION_POWER_FRACTION
    physics.bkwdPowerFraction = BKWD_POWER_FRACTION
    physics.gravity = g
    physics.cohesion = COHESION
    physics.riseFriction = RISE_FRICTION
    physics.riseFrictionY = RISE_FRICTION_Y
    physics.suspSlumpFriction = SUSP_SLUMP_FRICTION
    physics.slumpFrictionBound = SUSP_SLUMP_FRICTION_BOUND
    physics.fwdWrictionY = FWD_FRICTION_Y
    physics.maxSlipFrictionY = MAX_SLIP_FRICTION_Y
    physics.movementSignals = 0
    physics.leftFwdFrictionPt = Math.Vector3((-forcePtX * width, forcePtY, 0.0))
    physics.rightFwdFrictionPt = Math.Vector3((forcePtX * width, forcePtY, 0.0))
    coh = computeRotationalCohesion(wlim, fullMass, blen, width, physics.enginePower)
    physics.rotationalCohesion = coh
    physics.linMinPowerDivider = 1.0
    physics.rotMinPowerDivider = wlim * 0.1
    physics.springsHardFriction = TRACK_SIDE_FRICTION
    physics.springFwdFriction = TRACK_FWD_FRICTION
    physics.destructibleDamageFactor = 10
    physics.movementSignals = 0
    physics.tracksRestitution = TRACK_RESTITUTION
    speedLimit = max(fwdSpeedLimit, bkwdSpeedLimit)
    physics.continuumResistSpeed = CONTINUUM_RESIST_SPEED * speedLimit
    physics.continuumResist = CONTINUUM_RESIST / speedLimit
    physics.minSpeedAffectRot = MIN_SPEED_AFFECT_ROT
    physics.speedAffectRotBound = wlim * SPEED_AFFECT_ROT_DECREASE
    physics.speedAffectRot = physics.speedAffectRotBound / (MAX_SPEED_AFFECT_ROT - MIN_SPEED_AFFECT_ROT)
    terrRes = physDescr['terrainResistance']
    groundResistances = Math.Vector4(terrRes[0], terrRes[0], terrRes[1], terrRes[2])
    physics.groundResistances = groundResistances
    physics.cohDecayY = _COH_DECAY_Y
    physics.cohDecayFactor = _COH_DECAY_FACTOR
    physics.cohDecayPow = _COH_DECAY_POW / 2.0
    physics.cohDecayBound = _COH_DECAY_BOUND
    physics.strafeThreshold = _STRAFE_THRESHOLD
    physics.freezeAccelEpsilon = FREEZE_ACCEL_EPSILON
    physics.freezeAngAccelEpsilon = FREEZE_ANG_ACCEL_EPSILON
    physics.freezeVelEpsilon = FREEZE_VEL_EPSILON
    physics.freezeAngVelEpsilon = FREEZE_ANG_VEL_EPSILON
    physics.simulationYBound = _SIMULATION_Y_BOUND
    physics.removeAllDamperSprings()
    clearanceRatio = width / clearance
    if width < WIDTH_VERY_LONG and (width < WIDTH_LONG or clearanceRatio < CLEARANCE_RATIO_LONG):
        carrierSpringPairs = NUM_SPRINGS_NORMAL
    else:
        carrierSpringPairs = NUM_SPRINGS_LONG
    length = carringSpringLength
    stiffness = hmg / (carrierSpringPairs * 2 * length * (1.0 - suspCompression))
    suspDamp = _computeSuspDamp(fullMass) * stiffness
    trackLen = _computeTrackLength(clearance, blen)
    indent = boxHeight / 2
    sdir = Math.Vector3((0, -1, 0))
    stepZ = trackLen / (carrierSpringPairs - 1)
    begZ = -trackLen * 0.5
    leftX = -width * 0.45
    rightX = width * 0.45
    y = -boxHeight / 2 + boxCenter.y
    rollerMass = suspMass / (carrierSpringPairs * 2)
    rside = Math.Vector3((1, 0, 0))
    lside = -rside
    pen = TRACKS_PENETRATION
    rollerMode = ROLLER_MODE
    for i in xrange(0, carrierSpringPairs):
        climbFriction = SUSP_CLIMB_FRICTION if i == 0 or i == carrierSpringPairs - 1 else 0.0
        climbDirAxis = (0.0, 0.0, -1.0 if i == 0 else 1.0)
        climbFrictionDir = (sdir * lside).dot(climbDirAxis)
        mountPoint = Math.Vector3((leftX, y, begZ + i * stepZ))
        physics.addDamperSpring((mountPoint,
         sdir,
         lside,
         length,
         indent,
         hardRatio,
         stiffness,
         suspDamp,
         rollerMass,
         True,
         pen,
         rollerMode,
         climbFriction,
         climbFrictionDir))
        climbFrictionDir = -climbFrictionDir
        mountPoint = Math.Vector3((rightX, y, begZ + i * stepZ))
        physics.addDamperSpring((mountPoint,
         sdir,
         rside,
         length,
         indent,
         hardRatio,
         stiffness,
         suspDamp,
         rollerMass,
         False,
         pen,
         rollerMode,
         climbFriction,
         climbFrictionDir))

    if _LOG_INIT_PARAMS:
        LOG_DEBUG('initVehiclePhysics: clearance %f' % (clearance / height))
        LOG_DEBUG('initVehiclePhysics: suspMass %f' % _computeSuspWeightRatio(srcMass, srcEnginePower))
        LOG_DEBUG('initVehiclePhysics: trackLen %f' % (trackLen / blen))
        LOG_DEBUG('initVehiclePhysics: clearanceRatio %f' % (clearance / blen))
        LOG_DEBUG('initVehiclePhysics: hardRatio %f' % hardRatio)
        LOG_DEBUG('initVehiclePhysics: cmShift %f' % cmShift)
        LOG_DEBUG('initVehiclePhysics: suspCompression: %f' % suspCompression)


def computeBarrelLocalPoint(vehDescr, turretYaw, gunPitch):
    maxGunZ = vehDescr.gun['hitTester'].bbox[1][2]
    m = Math.Matrix()
    m.setRotateX(gunPitch)
    pt = m.applyVector((0.0, 0.0, maxGunZ)) + vehDescr.turret['gunPosition']
    m.setRotateY(turretYaw)
    pt = m.applyVector(pt)
    pt += vehDescr.hull['turretPositions'][vehDescr.activeTurretPosition]
    pt += vehDescr.chassis['hullPosition']
    return pt


def encodeAngleToUint(angle, bits):
    return int(((1 << bits) - 1) * (angle + pi) / (pi * 2.0))


def decodeAngleFromUint(code, bits):
    return pi * 2.0 * code / ((1 << bits) - 1) - pi


def linearInterpolate(arg, argMin, argMax, valMin, valMax):
    argRange = argMax - argMin
    narg = (arg - argMin) / argRange
    narg = _clamp(0.0, narg, 1.0)
    valRange = valMax - valMin
    val = narg * valRange + valMin
    return val


def _computeSuspDamp(mass):
    k = (mass - SUSP_DAMP_MASS_MIN) / (SUSP_DAMP_MASS_MAX - SUSP_DAMP_MASS_MIN)
    k = _clamp(0.0, k, 1.0)
    damp = k * (SUSP_DAMP_MAX - SUSP_DAMP_MIN) + SUSP_DAMP_MIN
    return damp


def _computeCenterOfMassShift(mass, enginePower):
    dr = enginePower / mass
    cmy = _powerCurve(dr, DYN_RATIO_MIN, DYN_RATIO_MID, DYN_RATIO_MAX, CMY_MIN, CMY_MID, CMY_MAX)
    return cmy


def _computeSuspWeightRatio(mass, enginePower):
    dr = enginePower / mass
    swRatio = _powerCurve(dr, DYN_RATIO_MIN, DYN_RATIO_MID, DYN_RATIO_MAX, SUSP_WEIGHT_MIN, SUSP_WEIGHT_MID, SUSP_WEIGHT_MAX)
    return swRatio


def _computeSuspCompression(mass):
    suspCompression = linearInterpolate(mass, SUSP_COMPRESSION_MIN_MASS, SUSP_COMPRESSION_MAX_MASS, SUSP_COMPRESSION_MIN, SUSP_COMPRESSION_MAX)
    return suspCompression


def _computeTrackLength(clearance, length):
    r = clearance / length
    lenRatio = linearInterpolate(r, CLEARANCE_TO_LENGTH_MIN, CLEARANCE_TO_LENGTH_MAX, TRACK_LENGTH_MAX, TRACK_LENGTH_MIN)
    return lenRatio * length


def _computeHardRatio(clearance, length):
    r = clearance / length
    return linearInterpolate(r, CLEARANCE_TO_LENGTH_MIN, CLEARANCE_TO_LENGTH_MAX, HARD_RATIO_MIN, HARD_RATIO_MAX)


def _powerCurve(arg, argMin, argMid, argMax, valMin, valMid, valMax):
    argRange = argMax - argMin
    narg = (arg - argMin) / argRange
    narg = _clamp(0.0, narg, 1.0)
    nargMid = (argMid - argMin) / argRange
    valRange = valMax - valMin
    nvalMid = (valMid - valMin) / valRange
    pow = math.log(nvalMid, nargMid)
    nval = math.pow(narg, pow)
    val = nval * valRange + valMin
    return val


def _clamp(minBound, arg, maxBound):
    return max(minBound, min(maxBound, arg))


def _encodeTurretDescr(vehicle):
    typeDescr = vehicle.typeDescriptor
    nationID, vehID = typeDescr.type.id
    turretPos = typeDescr.activeTurretPosition
    turretIdxs = tuple((desc['id'][1] for desc in typeDescr.turrets[turretPos]))
    turretIdx = turretIdxs.index(typeDescr.turret['id'][1])
    gunIdxs = tuple((desc['id'][1] for desc in typeDescr.turret['guns']))
    gunIdx = gunIdxs.index(typeDescr.gun['id'][1])
    descr = (nationID & 15) << 24
    descr |= (vehID & 65535) << 8
    descr |= (turretPos & 7) << 5
    descr |= (turretIdx & 3) << 3
    descr |= gunIdx & 7
    return descr


def _decodeTurretDescr(descr):
    nationID = descr >> 24 & 15
    vehID = descr >> 8 & 65535
    turretPos = descr >> 5 & 7
    turretIdx = descr >> 3 & 3
    gunIdx = descr & 7
    return (nationID,
     vehID,
     turretPos,
     turretIdx,
     gunIdx)


def initVehiclePhysicsFromParams(physics, params):

    class _SimpleObject(object):
        pass

    typeDesc = _SimpleObject()
    typeDesc.physics = {}
    typeDesc.physics['weight'] = params['weight']
    typeDesc.physics['enginePower'] = params['enginePower']
    typeDesc.physics['speedLimits'] = params['speedLimits']
    typeDesc.physics['rotationIsAroundCenter'] = params['rotationIsAroundCenter']
    typeDesc.physics['rotationSpeedLimit'] = params['rotationSpeedLimit']
    typeDesc.physics['terrainResistance'] = params['terrainResistance']
    typeDesc.physics['trackCenterOffset'] = params['trackCenterOffset']
    typeDesc.hull = {}
    typeDesc.hull['hitTester'] = _SimpleObject()
    typeDesc.hull['hitTester'].bbox = (params['hullHitTesterMin'], params['hullHitTesterMax'], None)
    typeDesc.hull['turretPositions'] = (params['turretPosition'],)
    typeDesc.chassis = {}
    typeDesc.chassis['hullPosition'] = params['hullPosition']
    typeDesc.chassis['hitTester'] = _SimpleObject()
    typeDesc.chassis['hitTester'].bbox = (params['chassisHitTesterMin'], params['chassisHitTesterMax'], None)
    typeDesc.turret = {}
    typeDesc.turret['hitTester'] = _SimpleObject()
    typeDesc.turret['hitTester'].bbox = (params['turretHitTesterMin'], params['turretHitTesterMax'], None)
    typeDesc.turret['gunPosition'] = params['gunPosition']
    initVehiclePhysics(physics, typeDesc)
    physics.visibilityMask = 4294967295L
    return
