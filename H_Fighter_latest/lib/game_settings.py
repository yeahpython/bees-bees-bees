import os
import pickle

# Life and death
ACID = "Wall Acid"
TOO_SLOW = "'Too Slow' Threshold"
HEALTH_LOSS_RATE = "Health Loss Rate"
HEALTH_GAIN = "Health Gain"
MAXIMUM_BEES = "Overpopulation Limit"
SLOWNESS_PENALTY = "Slowness Penalty"
SPEED_PAYOFF = "Speed Payoff"
MAX_HEALTH = "Maximum Health"

# Mutation
MUTATION_CHANCES = "Mutation Chances"
SCALING_MUTATION = "Scaling Mutation Rate"
ADDITIVE_MUTATION_RATE = "Additive Mutation Rate"
INVERT_MUTATION_RATE = "Invert Mutation Rate"
OFFSPRING_MUTATION_RATE = "Offspring Mutation Rate"
EYE_MUTATION_RANGE = "Eye Mutation Range"

# Topology / Physics
STING_REPULSION = "Sting Repulsion"
AUTOMATIC_EVASION = "Automatic Bee Evasion"
SWARMING_PEER_PRESSURE = "Swarming Peer Pressure"
WRAPAROUND_TRACKING = "Wraparound Tracking"
STICKY_WALLS = "Sticky Walls"
CREATURE_MODE = "Creature Mode"
COST_OF_JUMP = "Cost of Jumping"
GRAVITY = "Gravity"

# Variables controlling visual style
JUICINESS = "Juiciness"
SHOW_EYES = "Show Eyes"
SHOW_NAMES = "Show Names"

# Variables determining random map generation
GENERATE_RANDOM_MAP = "Generate Random Map"
RANDOM_TILE_DENSITY = "Random Tile Density"
CONGEAL_THOROUGHNESS = "Congeal Thoroughness"
RANDOM_MAP_LOW = "Tile Minimum Neighbors"
RANDOM_MAP_HIGH = "Tile Maximum Neighbors"
RANDOM_MAP_RUNS = "Mapgen iterations"
RANDOM_MAP_RADIUS = "Mapgen Neighborhood radius"

#Brain Types
SENSITIVITY_TO_PLAYER = "Sensitivity To Player Position"
BRAIN_BIAS = "Brain Bias"
MEMORY_STRENGTH = "Memory Strength"
BRAIN_ACTIVATION = "Brain Activation"

#Family Tree
TREE_V_SPACING = "Tree Vertical Spacing"
TREE_H_SPACING = "Tree Horizontal Spacing"
TREE_THICKNESS = "Tree Thickness"
TREE_COLOR_VARIATION = "Tree Color Variation"
TREE_UPDATE_TIME = "Tree Update Time"

SPECIES_STYLE = "Species Visualization Style"
BEE_STYLE = "Bee Style"

# Misc.
SHOW_HELP = "Show Help"

settings = {
ACID : 0.3,
TOO_SLOW : 0.03,
HEALTH_LOSS_RATE : 0.1 / 1000,
HEALTH_GAIN : 0.1,
MAXIMUM_BEES : 60,
SLOWNESS_PENALTY : 0.05,
MUTATION_CHANCES : 1,
SCALING_MUTATION : 0.5,
ADDITIVE_MUTATION_RATE : 0.05,
INVERT_MUTATION_RATE : 0.01,
JUICINESS : 0,
GENERATE_RANDOM_MAP : False,
SHOW_EYES : False,
SPEED_PAYOFF : 0.3,
OFFSPRING_MUTATION_RATE : 0.7,
STING_REPULSION : 15.0,
AUTOMATIC_EVASION : True,
SWARMING_PEER_PRESSURE : -0.3,
WRAPAROUND_TRACKING : True,
EYE_MUTATION_RANGE : 10,
STICKY_WALLS : 0,
SENSITIVITY_TO_PLAYER : 300,
SHOW_HELP : 1,
SHOW_NAMES : 1,
CREATURE_MODE : 1,
COST_OF_JUMP : 0.1,
BRAIN_BIAS : 10,
BRAIN_ACTIVATION : 1,
MEMORY_STRENGTH : 0.1,
RANDOM_TILE_DENSITY : 0.11,
CONGEAL_THOROUGHNESS : 0.4,
RANDOM_MAP_LOW : 10,
RANDOM_MAP_HIGH : 13,
RANDOM_MAP_RUNS : 5,
RANDOM_MAP_RADIUS : 5,
GRAVITY : 0.0006,
MAX_HEALTH : 2,
TREE_V_SPACING : 5,
TREE_H_SPACING : 5,
TREE_THICKNESS : 1,
TREE_COLOR_VARIATION: 100,
TREE_UPDATE_TIME: 10,
SPECIES_STYLE: 1,
BEE_STYLE: 2,
}

want_bools = [
GENERATE_RANDOM_MAP,
SHOW_EYES,
AUTOMATIC_EVASION,
WRAPAROUND_TRACKING,
SHOW_NAMES,
SHOW_HELP]

want_ints = [
MAXIMUM_BEES,
JUICINESS,
EYE_MUTATION_RANGE,
CREATURE_MODE,
RANDOM_MAP_LOW,
RANDOM_MAP_HIGH,
RANDOM_MAP_RUNS,
RANDOM_MAP_RADIUS,
TREE_THICKNESS,
TREE_H_SPACING,
TREE_V_SPACING,
TREE_UPDATE_TIME,
SPECIES_STYLE,
BEE_STYLE,
BRAIN_ACTIVATION,
]

max_val = {
HEALTH_GAIN: 1,
MUTATION_CHANCES: 1,
INVERT_MUTATION_RATE: 1,
JUICINESS: 3,
OFFSPRING_MUTATION_RATE: 1,
SWARMING_PEER_PRESSURE: 0.5,
CREATURE_MODE: 1,
MEMORY_STRENGTH: 1,
RANDOM_TILE_DENSITY: 1,
CONGEAL_THOROUGHNESS: 1,
SPECIES_STYLE: 4,
BEE_STYLE: 2,
BRAIN_ACTIVATION: 3,
}

min_val = {
MUTATION_CHANCES: 0,
INVERT_MUTATION_RATE: 0,
JUICINESS: 0,
OFFSPRING_MUTATION_RATE: 0,
SENSITIVITY_TO_PLAYER: 0,
CREATURE_MODE: 0,
MEMORY_STRENGTH: 0,
RANDOM_TILE_DENSITY: 0,
CONGEAL_THOROUGHNESS: 0,
RANDOM_MAP_RADIUS: 1,
TREE_THICKNESS: 1,
TREE_V_SPACING: 1,
TREE_H_SPACING: 1,
SPECIES_STYLE: 1,
MAXIMUM_BEES: 1,
BEE_STYLE: 1,
BRAIN_ACTIVATION: 1,
TREE_UPDATE_TIME: 1,
}

def problem_with_setting(key, value):


	if key in want_bools and value not in [1, 0]:
		return "%s should be 0 or 1." % key

	elif key in want_ints and type(value) != int:
		return "%s shouldn't have a decimal point" % key

	elif key in max_val and value > max_val[key]:
		return "%s should be at most %s" % (key, max_val[key])

	elif key in min_val and value < min_val[key]:
		return "%s should be at least %s" % (key, min_val[key])

	else:
		return 0

def save_settings():
	g = open(os.path.join("data", "saved", "settings.txt"), "wb")
	pickle.dump(settings, g)
	g.close()

def load_settings():
	try:
		g = open(os.path.join("data", "saved", "settings.txt"))
		loaded_settings = pickle.load(g)
		print "\n\n* * * * * * Loaded Settings * * * * * *"
		
		for key, value in loaded_settings.iteritems():
			settings[key] = value
			print key, ":", str(value)
		g.close()
	except:
		print "Failed to load settings. (File may have been corrupted or empty.)"