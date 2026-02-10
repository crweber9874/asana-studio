"""
seed_poses.py — Comprehensive yoga pose database.
300+ poses with Sanskrit names, categories, difficulty, and tags.
Sources: Yoga Journal A-Z, expanded with variations, sides, and advanced asanas.
"""
import sqlite3
from database import get_connection

# ─── Category constants ────────────────────────────────────────────────
CAT_STANDING   = "Standing"
CAT_SEATED     = "Seated"
CAT_SUPINE     = "Supine"
CAT_PRONE      = "Prone"
CAT_ARM_BAL    = "Arm Balance"
CAT_INVERSION  = "Inversion"
CAT_BALANCE    = "Balance"
CAT_CORE       = "Core"
CAT_RESTORATIVE = "Restorative"
CAT_KNEELING   = "Kneeling"

# ─── Pose data: (english, sanskrit, category, difficulty, hold_sec, bilateral, tags[], description) ──
# bilateral = True means L/R sides are generated automatically
POSES = [
    # ═══════════════════════════════════════════════
    # STANDING POSES
    # ═══════════════════════════════════════════════
    ("Mountain Pose", "Tadasana", CAT_STANDING, 1, 30, False,
     ["foundation", "standing"],
     "The foundation of all standing poses. Stand tall with feet together, weight evenly distributed, arms at sides."),

    ("Upward Salute", "Urdhva Hastasana", CAT_STANDING, 1, 15, False,
     ["standing", "chest-opener"],
     "From Mountain, sweep arms overhead, palms facing each other or touching, gentle backbend."),

    ("Standing Forward Bend", "Uttanasana", CAT_STANDING, 1, 30, False,
     ["forward-bend", "standing", "hamstring"],
     "Fold forward from the hips, releasing crown of head toward the floor."),

    ("Standing Half Forward Bend", "Ardha Uttanasana", CAT_STANDING, 1, 10, False,
     ["forward-bend", "standing"],
     "Halfway lift with flat back, fingertips on shins or floor, gaze forward."),

    ("Chair Pose", "Utkatasana", CAT_STANDING, 2, 30, False,
     ["standing", "strengthening", "core", "quad"],
     "Bend knees deeply as if sitting in an invisible chair, arms reaching overhead."),

    ("High Lunge", "Utthita Ashwa Sanchalanasana", CAT_STANDING, 2, 30, True,
     ["standing", "hip-opener", "strengthening"],
     "Deep lunge with back heel lifted, arms alongside ears, hips squared forward."),

    ("High Lunge Crescent", "Ashta Chandrasana", CAT_STANDING, 2, 30, True,
     ["standing", "hip-opener", "backbend"],
     "High lunge variation with slight backbend, arms sweeping overhead in a crescent shape."),

    ("Low Lunge", "Anjaneyasana", CAT_STANDING, 1, 30, True,
     ["standing", "hip-opener", "backbend"],
     "Back knee on the floor, front knee over ankle, arms overhead with gentle backbend."),

    ("Warrior I", "Virabhadrasana I", CAT_STANDING, 2, 30, True,
     ["standing", "strengthening", "hip-opener"],
     "Front knee bent 90°, back foot at 45°, arms overhead, hips squared forward."),

    ("Warrior II", "Virabhadrasana II", CAT_STANDING, 2, 30, True,
     ["standing", "strengthening", "hip-opener"],
     "Front knee bent 90°, arms extended parallel to floor, gaze over front fingertips."),

    ("Warrior III", "Virabhadrasana III", CAT_BALANCE, 3, 30, True,
     ["balancing", "strengthening", "standing"],
     "Balance on one leg, torso and lifted leg parallel to floor, arms reaching forward."),

    ("Reverse Warrior", "Viparita Virabhadrasana", CAT_STANDING, 2, 30, True,
     ["standing", "side-bend", "chest-opener"],
     "From Warrior II, drop back hand to back leg, front arm arcs overhead."),

    ("Extended Side Angle", "Utthita Parsvakonasana", CAT_STANDING, 2, 30, True,
     ["standing", "strengthening", "hip-opener"],
     "Front knee bent, bottom hand to floor or block outside front foot, top arm extends overhead."),

    ("Extended Triangle", "Utthita Trikonasana", CAT_STANDING, 2, 30, True,
     ["standing", "strengthening", "hamstring"],
     "Legs wide, front leg straight, hinge at hip to bring hand to shin/floor, top arm reaches up."),

    ("Revolved Side Angle", "Parivrtta Parsvakonasana", CAT_STANDING, 3, 30, True,
     ["standing", "twist", "strengthening"],
     "Deep lunge with twist, bottom hand outside front foot, top arm extends up or overhead."),

    ("Revolved Triangle", "Parivrtta Trikonasana", CAT_STANDING, 3, 30, True,
     ["standing", "twist", "strengthening", "hamstring"],
     "Standing twist with legs wide, hinge forward and rotate torso, opposite hand to floor."),

    ("Half Moon", "Ardha Chandrasana", CAT_BALANCE, 3, 30, True,
     ["balancing", "standing", "hip-opener"],
     "Balance on one leg with torso parallel to floor, top arm and leg extended."),

    ("Revolved Half Moon", "Parivrtta Ardha Chandrasana", CAT_BALANCE, 4, 30, True,
     ["balancing", "twist", "standing"],
     "Half Moon with a twist — bottom hand on floor, torso rotated open, top arm up."),

    ("Eagle Pose", "Garudasana", CAT_BALANCE, 3, 30, True,
     ["balancing", "standing", "hip-opener", "shoulder-opener"],
     "Single-leg balance with wrapped arms and legs, deep compression of joints."),

    ("Tree Pose", "Vrksasana", CAT_BALANCE, 1, 30, True,
     ["balancing", "standing", "hip-opener"],
     "Stand on one leg, opposite foot to inner thigh or calf (not knee), arms overhead or at heart."),

    ("Standing Split", "Urdhva Prasarita Eka Padasana", CAT_STANDING, 3, 30, True,
     ["standing", "forward-bend", "hamstring"],
     "Forward fold on one leg, opposite leg lifts as high as possible behind you."),

    ("Lord of the Dance", "Natarajasana", CAT_BALANCE, 4, 30, True,
     ["balancing", "backbend", "chest-opener"],
     "Balance on one leg, grab back foot with hand and press it up and back, front arm forward."),

    ("Extended Hand-to-Big-Toe", "Utthita Hasta Padangustasana", CAT_BALANCE, 3, 30, True,
     ["balancing", "standing", "hamstring"],
     "Standing balance, holding big toe with hand, extend leg forward then out to the side."),

    ("Garland Pose", "Malasana", CAT_STANDING, 2, 30, False,
     ["standing", "hip-opener"],
     "Deep squat with feet close together, elbows pressing knees open, palms together."),

    ("Goddess Pose", "Utkata Konasana", CAT_STANDING, 2, 30, False,
     ["standing", "hip-opener", "strengthening"],
     "Wide stance with toes turned out, deep bend in knees, arms in cactus or overhead."),

    ("Wide-Legged Forward Bend", "Prasarita Padottanasana", CAT_STANDING, 2, 30, False,
     ["standing", "forward-bend", "hamstring"],
     "Wide stance, hinge at hips, crown of head reaches toward the floor."),

    ("Wide-Legged Forward Bend A", "Prasarita Padottanasana A", CAT_STANDING, 2, 30, False,
     ["standing", "forward-bend", "hamstring"],
     "Hands to floor between feet, crown of head reaching toward the floor."),

    ("Wide-Legged Forward Bend B", "Prasarita Padottanasana B", CAT_STANDING, 2, 30, False,
     ["standing", "forward-bend", "hamstring"],
     "Hands on hips, fold forward maintaining a long spine."),

    ("Wide-Legged Forward Bend C", "Prasarita Padottanasana C", CAT_STANDING, 2, 30, False,
     ["standing", "forward-bend", "shoulder-opener"],
     "Hands clasped behind back, fold forward letting arms fall overhead."),

    ("Wide-Legged Forward Bend D", "Prasarita Padottanasana D", CAT_STANDING, 2, 30, False,
     ["standing", "forward-bend", "hamstring"],
     "Grab big toes with peace fingers, fold deeply."),

    ("Intense Side Stretch", "Parsvottanasana", CAT_STANDING, 2, 30, True,
     ["standing", "forward-bend", "hamstring"],
     "Pyramid pose — legs in short stance, fold over front leg with hands in reverse prayer."),

    ("Gate Pose", "Parighasana", CAT_KNEELING, 2, 30, True,
     ["side-bend", "hip-opener"],
     "Kneeling side bend with one leg extended, arm overhead creating a long lateral stretch."),

    ("Mountain Pose Arms Overhead", "Urdhva Tadasana", CAT_STANDING, 1, 15, False,
     ["standing", "foundation"],
     "Mountain Pose with arms actively reaching overhead, palms facing in."),

    ("Star Pose", "Utthita Tadasana", CAT_STANDING, 1, 15, False,
     ["standing", "foundation"],
     "Wide stance with arms extended horizontally, creating a five-pointed star shape."),

    ("Horse Pose", "Vatayanasana", CAT_STANDING, 4, 30, True,
     ["standing", "hip-opener", "balancing"],
     "Advanced half-lotus balance with deep knee bend and twist."),

    ("Dancer's Pose Full", "Natarajasana II", CAT_BALANCE, 5, 30, True,
     ["balancing", "backbend", "chest-opener"],
     "Full expression of Dancer with both hands grasping the back foot overhead."),

    # ═══════════════════════════════════════════════
    # SUN SALUTATION COMPONENTS
    # ═══════════════════════════════════════════════
    ("Sun Salutation A — Full", "Surya Namaskar A", CAT_STANDING, 2, 0, False,
     ["flow", "vinyasa", "sun-salutation"],
     "Complete Sun Salutation A sequence: Mountain → Upward Salute → Forward Fold → Half Lift → Chaturanga → Upward Dog → Downward Dog."),

    ("Sun Salutation B — Full", "Surya Namaskar B", CAT_STANDING, 3, 0, False,
     ["flow", "vinyasa", "sun-salutation"],
     "Complete Sun Salutation B sequence: Chair → Forward Fold → Half Lift → Chaturanga → Upward Dog → Downward Dog → Warrior I (R) → Vinyasa → Warrior I (L) → Vinyasa → Downward Dog."),

    # ═══════════════════════════════════════════════
    # SEATED POSES
    # ═══════════════════════════════════════════════
    ("Easy Pose", "Sukhasana", CAT_SEATED, 1, 60, False,
     ["seated", "hip-opener", "meditation"],
     "Simple cross-legged seat, spine tall, hands on knees."),

    ("Staff Pose", "Dandasana", CAT_SEATED, 1, 30, False,
     ["seated", "foundation"],
     "Seated with legs extended forward, spine tall, hands pressing beside hips."),

    ("Seated Forward Bend", "Paschimottanasana", CAT_SEATED, 2, 45, False,
     ["seated", "forward-bend", "hamstring"],
     "Fold forward over extended legs, reaching for feet or shins."),

    ("Head-to-Knee Forward Bend", "Janu Sirsasana", CAT_SEATED, 2, 30, True,
     ["seated", "forward-bend", "hamstring"],
     "One leg extended, other foot to inner thigh, fold over the straight leg."),

    ("Revolved Head-to-Knee", "Parivrtta Janu Sirsasana", CAT_SEATED, 3, 30, True,
     ["seated", "twist", "side-bend"],
     "From Janu Sirsasana position, rotate torso and reach for extended foot from the side."),

    ("Bound Angle Pose", "Baddha Konasana", CAT_SEATED, 1, 45, False,
     ["seated", "hip-opener"],
     "Soles of feet together, knees dropping to sides, seated butterfly stretch."),

    ("Reclining Bound Angle", "Supta Baddha Konasana", CAT_SUPINE, 1, 60, False,
     ["restorative", "hip-opener", "supine"],
     "Lying back with soles of feet together, knees open, arms relaxed at sides."),

    ("Wide-Angle Seated Forward Bend", "Upavistha Konasana", CAT_SEATED, 2, 45, False,
     ["seated", "forward-bend", "hip-opener"],
     "Legs spread wide, fold forward with hands walking out or reaching for feet."),

    ("Lotus Pose", "Padmasana", CAT_SEATED, 3, 60, False,
     ["seated", "hip-opener", "meditation"],
     "Cross-legged with each foot on the opposite thigh, spine tall."),

    ("Half Lotus", "Ardha Padmasana", CAT_SEATED, 2, 60, True,
     ["seated", "hip-opener", "meditation"],
     "One foot on opposite thigh, other leg in simple cross. Foundation for seated meditation."),

    ("Hero Pose", "Virasana", CAT_KNEELING, 2, 45, False,
     ["seated", "quad"],
     "Kneeling with sit bones between heels, tops of feet on floor."),

    ("Reclining Hero", "Supta Virasana", CAT_SUPINE, 3, 45, False,
     ["supine", "quad", "backbend"],
     "From Hero Pose, lean back to rest on elbows or fully recline on the floor."),

    ("Cow Face Pose", "Gomukhasana", CAT_SEATED, 3, 30, True,
     ["seated", "hip-opener", "shoulder-opener"],
     "Knees stacked, one arm reaching behind from above, other from below, clasping hands."),

    ("Fire Log Pose", "Agnistambhasana", CAT_SEATED, 3, 45, True,
     ["seated", "hip-opener"],
     "Shins stacked on top of each other, one knee over opposite ankle, fold forward."),

    ("Heron Pose", "Krounchasana", CAT_SEATED, 3, 30, True,
     ["seated", "hamstring"],
     "One leg folded back, other leg raised vertically holding foot, spine tall."),

    ("Bharadvaja's Twist", "Bharadvajasana I", CAT_SEATED, 2, 30, True,
     ["seated", "twist", "hip-opener"],
     "Seated twist with legs swept to one side, torso rotated opposite."),

    ("Half Lord of the Fishes", "Ardha Matsyendrasana", CAT_SEATED, 2, 30, True,
     ["seated", "twist", "hip-opener"],
     "Seated twist with one foot outside opposite knee, deep spinal rotation."),

    ("Marichi's Pose I", "Marichyasana I", CAT_SEATED, 3, 30, True,
     ["seated", "forward-bend", "bind"],
     "One knee bent foot flat, forward bend over straight leg, binding around bent knee."),

    ("Marichi's Pose III", "Marichyasana III", CAT_SEATED, 3, 30, True,
     ["seated", "twist", "bind"],
     "Seated twist with bind, one knee bent, rotating toward the bent knee side."),

    ("Monkey Pose", "Hanumanasana", CAT_SEATED, 5, 30, True,
     ["seated", "hamstring", "hip-opener"],
     "Full front splits, torso upright, arms reaching overhead or hands to floor."),

    ("Compass Pose", "Parivrtta Surya Yantrasana", CAT_SEATED, 5, 30, True,
     ["seated", "hamstring", "hip-opener", "twist"],
     "Seated with one leg behind shoulder, opposite hand grabs foot, other hand to floor."),

    ("Boat Pose", "Paripurna Navasana", CAT_CORE, 3, 30, False,
     ["core", "seated", "strengthening"],
     "Balance on sit bones, legs and torso forming a V shape, arms parallel to floor."),

    ("Half Boat Pose", "Ardha Navasana", CAT_CORE, 2, 30, False,
     ["core", "seated", "strengthening"],
     "Lower variation of Boat with legs and torso closer to the floor and more intense core engagement."),

    ("Scale Pose", "Tolasana", CAT_ARM_BAL, 4, 15, False,
     ["arm-balance", "core", "strengthening"],
     "From Lotus, press hands into floor and lift entire body off the ground."),

    ("Rope Pose", "Pasasana", CAT_SEATED, 4, 30, True,
     ["seated", "twist", "bind"],
     "Deep squat with twist and bind, wrapping arms around bundled knees."),

    # ═══════════════════════════════════════════════
    # PRONE POSES (face-down)
    # ═══════════════════════════════════════════════
    ("Cobra Pose", "Bhujangasana", CAT_PRONE, 1, 30, False,
     ["backbend", "chest-opener", "prone"],
     "Lying face down, press hands into floor to lift chest, elbows slightly bent."),

    ("Upward-Facing Dog", "Urdhva Mukha Svanasana", CAT_PRONE, 2, 15, False,
     ["backbend", "chest-opener", "prone"],
     "Press up with arms straight, thighs and shins lifted off floor, chest open."),

    ("Sphinx Pose", "Salamba Bhujangasana", CAT_PRONE, 1, 45, False,
     ["backbend", "chest-opener", "restorative"],
     "Forearms on floor, elbows under shoulders, gentle chest lift. Restorative backbend."),

    ("Locust Pose", "Salabhasana", CAT_PRONE, 2, 20, False,
     ["backbend", "strengthening", "prone"],
     "Lying face down, lift chest, arms, and legs off the floor simultaneously."),

    ("Bow Pose", "Dhanurasana", CAT_PRONE, 3, 20, False,
     ["backbend", "chest-opener", "prone"],
     "Grab ankles behind you, press feet into hands to lift chest and thighs off floor."),

    ("Half Frog Pose", "Ardha Bhekasana", CAT_PRONE, 3, 30, True,
     ["backbend", "quad", "prone"],
     "Lying prone, bend one knee and press foot toward hip with same side hand."),

    ("Full Frog Pose", "Bhekasana", CAT_PRONE, 4, 30, False,
     ["backbend", "quad", "prone"],
     "Both knees bent, both hands pressing feet toward hips, chest lifted."),

    ("Crocodile Pose", "Makarasana", CAT_PRONE, 1, 60, False,
     ["restorative", "prone"],
     "Prone relaxation pose, forehead on stacked hands, legs extended and relaxed."),

    # ═══════════════════════════════════════════════
    # SUPINE POSES (face-up)
    # ═══════════════════════════════════════════════
    ("Corpse Pose", "Savasana", CAT_RESTORATIVE, 1, 300, False,
     ["restorative", "supine", "meditation"],
     "Final resting pose. Lie flat on back, arms and legs relaxed, palms up, eyes closed."),

    ("Happy Baby", "Ananda Balasana", CAT_SUPINE, 1, 45, False,
     ["supine", "hip-opener", "restorative"],
     "On back, grab outer edges of feet, knees wide toward armpits."),

    ("Reclining Hand-to-Big-Toe", "Supta Padangusthasana", CAT_SUPINE, 2, 30, True,
     ["supine", "hamstring"],
     "Lying on back, extend one leg up and hold the big toe, other leg grounded."),

    ("Bridge Pose", "Setu Bandha Sarvangasana", CAT_SUPINE, 2, 30, False,
     ["backbend", "chest-opener", "strengthening"],
     "Lying on back, feet flat, press hips up toward the ceiling, clasp hands under back."),

    ("Wheel Pose", "Urdhva Dhanurasana", CAT_SUPINE, 4, 15, False,
     ["backbend", "chest-opener", "strengthening"],
     "Full backbend pressing up from the floor, hands and feet planted, hips lifting high."),

    ("One-Legged Wheel", "Eka Pada Urdhva Dhanurasana", CAT_SUPINE, 5, 10, True,
     ["backbend", "balancing", "strengthening"],
     "Full Wheel with one leg extended straight up toward the ceiling."),

    ("Upward Facing Two-Foot Staff", "Dwi Pada Viparita Dandasana", CAT_SUPINE, 5, 15, False,
     ["backbend", "chest-opener", "inversion"],
     "Forearm backbend — a combination of headstand and wheel with forearms on the ground."),

    ("Fish Pose", "Matsyasana", CAT_SUPINE, 2, 30, False,
     ["backbend", "chest-opener", "supine"],
     "On back, lift chest by pressing onto elbows, crown of head lightly on floor."),

    ("Supine Spinal Twist", "Supta Matsyendrasana", CAT_SUPINE, 1, 30, True,
     ["supine", "twist", "restorative"],
     "Lying on back, draw one knee across body, arms in T, gaze toward opposite hand."),

    ("Legs-Up-the-Wall", "Viparita Karani", CAT_RESTORATIVE, 1, 300, False,
     ["restorative", "inversion", "supine"],
     "Sit close to a wall, swing legs up the wall, rest with arms at sides."),

    ("Upward Plank", "Purvottanasana", CAT_SUPINE, 3, 20, False,
     ["strengthening", "chest-opener"],
     "Reverse plank — press hips up with hands behind, chest open, legs straight."),

    ("Side-Reclining Leg Lift", "Anantasana", CAT_SUPINE, 3, 30, True,
     ["balancing", "core", "hamstring"],
     "Lying on one side, bottom arm supports head, top leg extends up holding big toe."),

    ("Wind-Relieving Pose", "Pavanamuktasana", CAT_SUPINE, 1, 30, True,
     ["supine", "hip-opener", "restorative"],
     "On back, hug one or both knees into chest, gentle rock side to side."),

    # ═══════════════════════════════════════════════
    # KNEELING POSES
    # ═══════════════════════════════════════════════
    ("Cat Pose", "Marjaryasana", CAT_KNEELING, 1, 10, False,
     ["kneeling", "core"],
     "On all fours, round spine up like a cat, tucking chin and tailbone."),

    ("Cow Pose", "Bitilasana", CAT_KNEELING, 1, 10, False,
     ["kneeling", "backbend"],
     "On all fours, drop belly, lift chest and tailbone, gaze up."),

    ("Cat-Cow Flow", "Marjaryasana-Bitilasana", CAT_KNEELING, 1, 20, False,
     ["kneeling", "flow", "core"],
     "Alternating between Cat and Cow poses, synchronized with breath."),

    ("Camel Pose", "Ustrasana", CAT_KNEELING, 3, 20, False,
     ["kneeling", "backbend", "chest-opener"],
     "Kneel with hips over knees, reach back to grab heels, press hips forward, open chest."),

    ("Extended Puppy Pose", "Uttana Shishosana", CAT_KNEELING, 1, 30, False,
     ["kneeling", "forward-bend", "chest-opener"],
     "From all fours, walk hands forward, melting chest toward floor, hips over knees."),

    ("Child's Pose", "Balasana", CAT_KNEELING, 1, 60, False,
     ["kneeling", "restorative", "forward-bend"],
     "Knees wide or together, sit back on heels, fold forward with arms extended or alongside body."),

    ("Thread the Needle", "Parsva Balasana", CAT_KNEELING, 1, 30, True,
     ["kneeling", "twist", "shoulder-opener"],
     "From all fours, slide one arm under the body, lowering shoulder to floor."),

    ("Bird Dog", "Dandayamna Bharmanasana", CAT_KNEELING, 2, 15, True,
     ["kneeling", "core", "balancing"],
     "On all fours, extend opposite arm and leg, engage core for stability."),

    ("Tiger Pose", "Vyaghrasana", CAT_KNEELING, 2, 15, True,
     ["kneeling", "backbend", "core"],
     "From all fours, extend one leg back and up, reach back with opposite hand to grab foot."),

    ("Pigeon Prep", "Eka Pada Rajakapotasana Prep", CAT_KNEELING, 2, 45, True,
     ["hip-opener", "kneeling"],
     "Front shin on floor, back leg extended behind, upright torso. Classic hip opener."),

    ("Sleeping Pigeon", "Eka Pada Rajakapotasana Variation", CAT_KNEELING, 2, 60, True,
     ["hip-opener", "forward-bend", "restorative"],
     "From Pigeon Prep, fold forward over front shin, arms extended, forehead to floor."),

    ("King Pigeon", "Eka Pada Rajakapotasana", CAT_KNEELING, 4, 30, True,
     ["hip-opener", "backbend", "chest-opener"],
     "From Pigeon Prep, bend back knee, reach back to grab foot, deep backbend."),

    ("One-Legged King Pigeon II", "Eka Pada Rajakapotasana II", CAT_KNEELING, 5, 30, True,
     ["hip-opener", "backbend"],
     "Advanced pigeon variation — back leg bends overhead to meet head, full backbend."),

    ("Mermaid Pose", "Naginyasana", CAT_KNEELING, 4, 30, True,
     ["hip-opener", "backbend", "chest-opener"],
     "Pigeon variation with back foot in elbow crease, arms clasped overhead."),

    ("Standing Pigeon", "Uttana Kapotasana", CAT_STANDING, 2, 30, True,
     ["standing", "hip-opener"],
     "Standing figure-four — ankle on opposite knee, sit back into a squat shape."),

    # ═══════════════════════════════════════════════
    # DOWNWARD DOG & VARIATIONS
    # ═══════════════════════════════════════════════
    ("Downward-Facing Dog", "Adho Mukha Svanasana", CAT_STANDING, 2, 30, False,
     ["standing", "forward-bend", "strengthening"],
     "Inverted V shape, hands and feet on floor, hips pressing up and back."),

    ("Three-Legged Dog", "Tri Pada Adho Mukha Svanasana", CAT_STANDING, 2, 20, True,
     ["standing", "hip-opener"],
     "Downward Dog with one leg extended up toward the ceiling."),

    ("Dolphin Pose", "Ardha Pincha Mayurasana", CAT_STANDING, 3, 30, False,
     ["inversion", "strengthening", "shoulder-opener"],
     "Forearm Downward Dog — forearms on floor, hips lifted, head between arms."),

    ("Wild Thing", "Camatkarasana", CAT_ARM_BAL, 3, 15, True,
     ["backbend", "chest-opener", "arm-balance"],
     "From side plank or Down Dog, flip open, one hand plants, hips lift, free arm reaches overhead."),

    # ═══════════════════════════════════════════════
    # PLANK VARIATIONS
    # ═══════════════════════════════════════════════
    ("Plank Pose", "Phalakasana", CAT_CORE, 2, 30, False,
     ["core", "strengthening", "arm-balance"],
     "Top of a push-up position, body in one straight line from head to heels."),

    ("Forearm Plank", "Makara Adho Mukha Svanasana", CAT_CORE, 2, 30, False,
     ["core", "strengthening"],
     "Plank on forearms, elbows under shoulders, body in a straight line."),

    ("Side Plank", "Vasisthasana", CAT_ARM_BAL, 3, 20, True,
     ["arm-balance", "core", "balancing"],
     "Balance on one hand and edge of bottom foot, body sideways, top arm reaches up."),

    ("Side Plank with Tree Legs", "Vasisthasana Variation", CAT_ARM_BAL, 3, 20, True,
     ["arm-balance", "core", "hip-opener"],
     "Side Plank with top foot placed on inner thigh of bottom leg in tree position."),

    ("Side Plank with Top Leg Extended", "Vasisthasana II", CAT_ARM_BAL, 4, 20, True,
     ["arm-balance", "core", "hamstring"],
     "Side Plank holding big toe of top leg extended upward."),

    ("Four-Limbed Staff", "Chaturanga Dandasana", CAT_CORE, 3, 10, False,
     ["core", "strengthening", "arm-balance"],
     "Low push-up position, elbows at 90°, body hovering just above the floor."),

    # ═══════════════════════════════════════════════
    # ARM BALANCES
    # ═══════════════════════════════════════════════
    ("Crow Pose", "Bakasana", CAT_ARM_BAL, 3, 15, False,
     ["arm-balance", "core"],
     "Squat, place hands on floor, lift feet by pressing knees onto backs of upper arms."),

    ("Crane Pose", "Bakasana Full", CAT_ARM_BAL, 4, 15, False,
     ["arm-balance", "core"],
     "Like Crow but with arms fully straight, a more advanced expression."),

    ("Side Crow", "Parsva Bakasana", CAT_ARM_BAL, 4, 15, True,
     ["arm-balance", "twist", "core"],
     "Twist and balance both legs on one arm shelf, body perpendicular to the floor."),

    ("Flying Crow", "Eka Pada Galavasana", CAT_ARM_BAL, 5, 15, True,
     ["arm-balance", "hip-opener", "core"],
     "Figure-four on the arms — one shin on upper arms, back leg extended behind."),

    ("Eight-Angle Pose", "Astavakrasana", CAT_ARM_BAL, 4, 15, True,
     ["arm-balance", "core", "twist"],
     "Legs wrapped around one arm, body tilted sideways in an arm balance."),

    ("Firefly Pose", "Tittibhasana", CAT_ARM_BAL, 4, 15, False,
     ["arm-balance", "hamstring", "core"],
     "Arms between legs, lift up and extend legs forward, balancing on hands."),

    ("Shoulder-Pressing Pose", "Bhujapidasana", CAT_ARM_BAL, 3, 15, False,
     ["arm-balance", "hip-opener"],
     "Squat, wrap legs around upper arms, lift feet and cross ankles."),

    ("Peacock Pose", "Mayurasana", CAT_ARM_BAL, 5, 15, False,
     ["arm-balance", "core", "strengthening"],
     "Balance horizontally on bent elbows pressed into abdomen, legs extended straight back."),

    ("Grasshopper Pose", "Parsva Bhuja Dandasana", CAT_ARM_BAL, 5, 15, True,
     ["arm-balance", "twist", "hip-opener"],
     "Deep twist arm balance — one leg over opposite arm, back leg extended, hovering."),

    ("Fallen Angel", "Devaduuta Panna Asana", CAT_ARM_BAL, 4, 15, True,
     ["arm-balance", "twist", "core"],
     "Side Crow variation — roll onto the temple, one arm shelf, legs extended sideways."),

    ("Pose Dedicated to Sage Koundinya I", "Eka Pada Koundinyanasana I", CAT_ARM_BAL, 5, 15, True,
     ["arm-balance", "twist"],
     "Twisted arm balance with legs split — front leg on top arm, back leg extended."),

    ("Pose Dedicated to Sage Koundinya II", "Eka Pada Koundinyanasana II", CAT_ARM_BAL, 5, 15, True,
     ["arm-balance", "hip-opener"],
     "Arm balance with one leg extended forward over a straight arm, back leg extended behind."),

    ("Flying Pigeon", "Eka Pada Galavasana Variation", CAT_ARM_BAL, 5, 15, True,
     ["arm-balance", "hip-opener", "core"],
     "Figure-four balance on the arms with more upright torso and lifted back leg."),

    ("Pendant Pose", "Lolasana", CAT_ARM_BAL, 4, 10, False,
     ["arm-balance", "core"],
     "From crossed legs, press hands to floor, lift entire body and swing like a pendant."),

    ("Dragonfly Pose", "Maksikanagasana", CAT_ARM_BAL, 5, 15, True,
     ["arm-balance", "twist", "core"],
     "Advanced twist arm balance with wide-split legs."),

    # ═══════════════════════════════════════════════
    # INVERSIONS
    # ═══════════════════════════════════════════════
    ("Supported Headstand", "Salamba Sirsasana", CAT_INVERSION, 4, 60, False,
     ["inversion", "balancing", "strengthening"],
     "Balance on forearms and crown of head, body inverted vertically."),

    ("Tripod Headstand", "Sirsasana II", CAT_INVERSION, 4, 30, False,
     ["inversion", "balancing"],
     "Headstand balanced on crown and palms with elbows at 90°."),

    ("Supported Shoulderstand", "Salamba Sarvangasana", CAT_INVERSION, 3, 60, False,
     ["inversion", "restorative"],
     "Shoulders on floor, hands supporting the back, legs extending straight up."),

    ("Plow Pose", "Halasana", CAT_INVERSION, 3, 30, False,
     ["inversion", "forward-bend"],
     "From Shoulderstand, lower feet to floor behind head, arms extending back."),

    ("Feathered Peacock", "Pincha Mayurasana", CAT_INVERSION, 5, 20, False,
     ["inversion", "balancing", "strengthening"],
     "Forearm stand — balance inverted on forearms with legs extending straight up."),

    ("Handstand", "Adho Mukha Vrksasana", CAT_INVERSION, 5, 20, False,
     ["inversion", "balancing", "strengthening"],
     "Full handstand — balance on hands, body inverted, legs straight up."),

    ("Scorpion Pose (Forearm)", "Vrschikasana I", CAT_INVERSION, 5, 15, False,
     ["inversion", "backbend", "balancing"],
     "Forearm stand with deep backbend — legs curl overhead toward head."),

    ("Scorpion Pose (Handstand)", "Vrschikasana II", CAT_INVERSION, 5, 15, False,
     ["inversion", "backbend", "balancing"],
     "Handstand scorpion — balance on hands while curling legs overhead in deep backbend."),

    ("Headstand Lotus", "Urdhva Padmasana in Sirsasana", CAT_INVERSION, 5, 30, False,
     ["inversion", "hip-opener"],
     "Headstand with legs in Lotus position."),

    ("Shoulderstand Lotus", "Padma Sarvangasana", CAT_INVERSION, 4, 30, False,
     ["inversion", "hip-opener"],
     "Shoulderstand with legs folded in Lotus position."),

    # ═══════════════════════════════════════════════
    # CORE & STRENGTHENING
    # ═══════════════════════════════════════════════
    ("Bicycle Crunches", "Dwichakrikasana", CAT_CORE, 2, 30, False,
     ["core", "strengthening"],
     "Supine core work, alternating elbow to opposite knee in a cycling motion."),

    ("Boat to Low Boat Flow", "Navasana Vinyasa", CAT_CORE, 3, 15, False,
     ["core", "strengthening", "flow"],
     "Alternate between full Boat and Low Boat (hover) for intense core work."),

    ("Forearm Side Plank", "Vasisthasana Forearm", CAT_CORE, 2, 20, True,
     ["core", "strengthening"],
     "Side Plank on the forearm instead of the hand, more accessible variation."),

    ("Knee-to-Nose", "Adho Mukha Svanasana Variation", CAT_CORE, 2, 10, True,
     ["core", "strengthening"],
     "From Down Dog, draw one knee toward the nose, rounding the spine, engaging core."),

    ("Dolphin Push-Ups", "Ardha Pincha Push-Up", CAT_CORE, 3, 15, False,
     ["core", "strengthening", "shoulder-opener"],
     "From Dolphin, shift forward to forearm plank and back, building shoulder strength."),

    # ═══════════════════════════════════════════════
    # BACKBENDS
    # ═══════════════════════════════════════════════
    ("Pigeon Pose (Full)", "Kapotasana", CAT_KNEELING, 5, 20, False,
     ["backbend", "chest-opener", "hip-opener"],
     "Deep backbend from kneeling — hands reach back to grab feet by the head."),

    ("Wild Thing Full", "Camatkarasana Full", CAT_ARM_BAL, 4, 15, True,
     ["backbend", "chest-opener", "arm-balance"],
     "Full expression of Wild Thing with deep chest opening and back foot planted."),

    ("Upward Bow One-Arm", "Eka Hasta Urdhva Dhanurasana", CAT_SUPINE, 5, 10, True,
     ["backbend", "strengthening", "balancing"],
     "Wheel Pose with one arm lifted, balancing on one hand and two feet."),

    ("Little Thunderbolt", "Laghu Vajrasana", CAT_KNEELING, 4, 15, False,
     ["backbend", "quad", "strengthening"],
     "From kneeling, lean back until crown of head touches the floor, maintaining hip push."),

    ("King Cobra", "Raja Bhujangasana", CAT_PRONE, 4, 15, False,
     ["backbend", "chest-opener"],
     "Advanced Cobra with maximum back extension, feet reaching toward head."),

    # ═══════════════════════════════════════════════
    # ADDITIONAL STANDING & BALANCE
    # ═══════════════════════════════════════════════
    ("Bird of Paradise", "Svarga Dvijasana", CAT_BALANCE, 5, 20, True,
     ["balancing", "hip-opener", "hamstring", "bind"],
     "From a bound Extended Side Angle, stand up and extend the bound leg straight."),

    ("Revolved Bird of Paradise", "Parivrtta Svarga Dvijasana", CAT_BALANCE, 5, 20, True,
     ["balancing", "twist", "hamstring", "bind"],
     "Twisted version of Bird of Paradise, rotating the torso while maintaining the bind."),

    ("Toe Stand", "Padangusthasana (Balance)", CAT_BALANCE, 4, 20, True,
     ["balancing", "hip-opener"],
     "From Tree or Half Lotus, lower into a deep squat balancing on the ball of one foot."),

    ("Toppling Tree", "Patita Tarasana", CAT_BALANCE, 3, 20, True,
     ["balancing", "side-bend"],
     "Standing side bend on one leg, creating a long arc from foot to fingertips."),

    ("Sugarcane Pose", "Ardha Chandra Chapasana", CAT_BALANCE, 4, 20, True,
     ["balancing", "backbend", "quad"],
     "Half Moon variation — bend the top leg and grab the foot, adding a quad stretch and backbend."),

    ("Revolved Chair", "Parivrtta Utkatasana", CAT_STANDING, 3, 20, True,
     ["standing", "twist", "strengthening"],
     "Chair Pose with twist, elbow to outside of opposite knee, palms together."),

    ("Standing Backbend", "Anuvittasana", CAT_STANDING, 2, 15, False,
     ["standing", "backbend", "chest-opener"],
     "From Mountain, lean back gently with arms overhead, opening the chest."),

    ("Standing Side Bend", "Indudalasana", CAT_STANDING, 1, 15, True,
     ["standing", "side-bend"],
     "From Mountain with arms overhead, lean to one side creating a crescent shape."),

    ("Humble Warrior", "Baddha Virabhadrasana", CAT_STANDING, 3, 30, True,
     ["standing", "forward-bend", "shoulder-opener", "bind"],
     "From Warrior I, interlace hands behind back, fold forward inside the front knee."),

    ("Skandasana", "Skandasana", CAT_STANDING, 3, 20, True,
     ["standing", "hip-opener", "hamstring"],
     "Side lunge — one leg straight, one deeply bent, torso upright or slightly forward."),

    ("Lizard Pose", "Utthan Pristhasana", CAT_STANDING, 3, 45, True,
     ["hip-opener", "standing"],
     "Deep lunge with both hands inside the front foot, forearms optionally on floor."),

    ("Dragon Pose", "Utthan Pristhasana Deep", CAT_STANDING, 3, 45, True,
     ["hip-opener", "standing"],
     "Deeper variant of Lizard with forearms on the floor and back knee optionally lifted."),

    # ═══════════════════════════════════════════════
    # ADDITIONAL ADVANCED
    # ═══════════════════════════════════════════════
    ("Flying Splits", "Eka Pada Koundinyanasana II Variation", CAT_ARM_BAL, 5, 15, True,
     ["arm-balance", "hamstring"],
     "Arm balance with full leg split — one leg forward, one back, balanced on hands."),

    ("Destroyed Pose", "Bhairavasana", CAT_SEATED, 5, 15, True,
     ["hip-opener", "hamstring", "seated"],
     "Leg behind the head while seated, demonstrating extreme hip and hamstring flexibility."),

    ("Yogic Sleep Pose", "Yoganidrasana", CAT_SUPINE, 5, 30, False,
     ["hip-opener", "forward-bend", "supine"],
     "Both legs behind the head while lying supine, deep fold."),

    ("Embryo Pose", "Garbha Pindasana", CAT_SEATED, 5, 15, False,
     ["arm-balance", "core", "hip-opener"],
     "From Lotus, thread arms through legs and roll on the spine."),

    ("Tortoise Pose", "Kurmasana", CAT_SEATED, 4, 30, False,
     ["seated", "forward-bend", "hamstring"],
     "Seated with legs over arms, chest to floor, arms extending under legs."),

    ("Sleeping Tortoise", "Supta Kurmasana", CAT_SEATED, 5, 30, False,
     ["seated", "forward-bend", "hip-opener"],
     "Feet crossed behind head, arms bound behind back. Advanced version of Tortoise."),

    ("Splits Facing Forward", "Samakonasana", CAT_SEATED, 5, 30, False,
     ["hip-opener", "hamstring"],
     "Center (middle) splits, straddling wide with torso facing forward."),

    ("Handstand Scorpion", "Taraksvasana", CAT_INVERSION, 5, 10, False,
     ["inversion", "backbend"],
     "Handstand with scorpion legs — deep backbend overhead while balanced on hands."),

    ("One-Handed Tree", "Eka Hasta Vrksasana", CAT_INVERSION, 5, 10, True,
     ["inversion", "balancing"],
     "One-arm handstand balance — the ultimate expression of strength and balance."),

    ("Headstand Splits", "Urdhva Prasarita Eka Padasana in Sirsasana", CAT_INVERSION, 5, 15, False,
     ["inversion", "hamstring"],
     "Headstand with legs in a wide split."),

    # ═══════════════════════════════════════════════
    # RESTORATIVE / YIN EXTRAS
    # ═══════════════════════════════════════════════
    ("Supported Child's Pose", "Salamba Balasana", CAT_RESTORATIVE, 1, 120, False,
     ["restorative", "forward-bend"],
     "Child's Pose with a bolster under the torso for deeper relaxation."),

    ("Reclined Twist", "Supta Matsyendrasana B", CAT_RESTORATIVE, 1, 60, True,
     ["restorative", "twist", "supine"],
     "Gentle supine twist with knees to one side, arms in T position."),

    ("Banana Pose", "Bananasana", CAT_RESTORATIVE, 1, 120, True,
     ["restorative", "side-bend", "supine"],
     "Lying supine, shift hips and feet to one side creating a lateral crescent shape."),

    ("Supported Bridge", "Salamba Setu Bandhasana", CAT_RESTORATIVE, 1, 120, False,
     ["restorative", "backbend"],
     "Bridge with a block under the sacrum for passive support."),

    ("Caterpillar Pose", "Paschimottanasana Yin", CAT_RESTORATIVE, 1, 180, False,
     ["restorative", "forward-bend", "hamstring"],
     "Yin version of Seated Forward Bend — relaxed, rounded spine, held for minutes."),

    ("Dragonfly Yin", "Upavistha Konasana Yin", CAT_RESTORATIVE, 1, 180, False,
     ["restorative", "hip-opener", "hamstring"],
     "Yin version of Wide-Angle Forward Bend — relaxed, long-held stretch."),

    ("Saddle Pose", "Supta Vajrasana", CAT_RESTORATIVE, 2, 180, False,
     ["restorative", "quad", "backbend"],
     "Yin version of Reclining Hero — gentle backbend and quad stretch held for several minutes."),

    ("Shoelace Pose", "Gomukhasana Yin", CAT_RESTORATIVE, 2, 120, True,
     ["restorative", "hip-opener"],
     "Yin version of Cow Face Pose — stacked knees, fold forward, long hold."),

    ("Square Pose", "Agnistambhasana Yin", CAT_RESTORATIVE, 2, 120, True,
     ["restorative", "hip-opener"],
     "Yin version of Fire Log — stacked shins, fold forward, long hold."),

    ("Sphinx Yin", "Salamba Bhujangasana Yin", CAT_RESTORATIVE, 1, 180, False,
     ["restorative", "backbend"],
     "Yin version of Sphinx — passive backbend held for several minutes."),

    ("Seal Pose", "Bhujangasana Yin", CAT_RESTORATIVE, 2, 180, False,
     ["restorative", "backbend"],
     "Yin version with arms straight — deeper backbend than Sphinx Yin."),

    # ═══════════════════════════════════════════════
    # TWIST SPECIALS
    # ═══════════════════════════════════════════════
    ("Revolved Crescent Lunge", "Parivrtta Ashta Chandrasana", CAT_STANDING, 3, 30, True,
     ["standing", "twist", "hip-opener"],
     "High Lunge with twist — palms together, elbow to outside of front knee."),

    ("Prayer Twist in Chair", "Parivrtta Utkatasana Variation", CAT_STANDING, 3, 20, True,
     ["standing", "twist", "strengthening"],
     "Chair Pose with deeper twist, hands at heart center, elbow hooking outside knee."),

    ("Twisted Lizard", "Parivrtta Utthan Pristhasana", CAT_STANDING, 4, 30, True,
     ["hip-opener", "twist"],
     "From Lizard Pose, rotate torso open, top arm reaching up."),

    ("Supine Eagle Twist", "Supta Garudasana", CAT_SUPINE, 1, 30, True,
     ["supine", "twist", "hip-opener"],
     "Lying on back with legs in Eagle wrap, drop knees to one side for a twist."),

    # ═══════════════════════════════════════════════
    # BOUND & BIND POSES
    # ═══════════════════════════════════════════════
    ("Bound Extended Side Angle", "Baddha Utthita Parsvakonasana", CAT_STANDING, 4, 30, True,
     ["standing", "bind", "hip-opener"],
     "Extended Side Angle with a bind — bottom hand wraps under front thigh, top arm behind back."),

    ("Bound Half Moon", "Baddha Ardha Chandrasana", CAT_BALANCE, 4, 30, True,
     ["balancing", "bind", "hip-opener"],
     "Half Moon with a bind — standing hand wraps under thigh, top arm behind back."),

    ("Bound Triangle", "Baddha Trikonasana", CAT_STANDING, 4, 30, True,
     ["standing", "bind"],
     "Extended Triangle with a bind, wrapping arms through and around the front leg."),

    ("Bound Revolved Triangle", "Baddha Parivrtta Trikonasana", CAT_STANDING, 4, 30, True,
     ["standing", "twist", "bind"],
     "Revolved Triangle with bind for deeper twist and shoulder opening."),

    # ═══════════════════════════════════════════════
    # MISCELLANEOUS
    # ═══════════════════════════════════════════════
    ("Big Toe Pose", "Padangusthasana", CAT_STANDING, 2, 30, False,
     ["standing", "forward-bend", "hamstring"],
     "Standing forward fold gripping big toes with peace fingers, pulling torso toward legs."),

    ("Hand Under Foot Pose", "Padahastasana", CAT_STANDING, 2, 30, False,
     ["standing", "forward-bend", "hamstring"],
     "Standing forward fold with palms under feet, wrists at the toes."),

    ("Ear Pressure Pose", "Karnapidasana", CAT_INVERSION, 3, 30, False,
     ["inversion", "forward-bend"],
     "From Plow, bend knees to rest on ears, arms alongside body or clasped."),

    ("Embryo in Shoulderstand", "Pindasana in Sarvangasana", CAT_INVERSION, 4, 20, False,
     ["inversion", "hip-opener"],
     "Shoulderstand with Lotus, then fold into embryo shape."),

    ("Revolved Wide-Legged Forward Bend", "Parivrtta Prasarita Padottanasana", CAT_STANDING, 3, 30, True,
     ["standing", "twist", "forward-bend"],
     "Wide stance forward fold with one hand to floor, other arm twisting open."),

    ("Half Splits", "Ardha Hanumanasana", CAT_KNEELING, 2, 30, True,
     ["kneeling", "hamstring"],
     "Low lunge with front leg straightened, hips square, fold over front leg."),

    ("Full Splits Variation Arms Up", "Hanumanasana Variation", CAT_SEATED, 5, 30, True,
     ["seated", "hamstring", "hip-opener", "backbend"],
     "Full splits with arms reaching overhead, slight backbend for deeper opening."),

    ("Puppy Pose", "Anahatasana", CAT_KNEELING, 1, 30, False,
     ["kneeling", "chest-opener", "forward-bend"],
     "Knees on floor, walk arms forward until chest melts toward the floor, hips stay over knees."),

    ("Fallen Triangle", "Patita Tarasana", CAT_ARM_BAL, 4, 20, True,
     ["arm-balance", "twist", "hip-opener"],
     "From side plank, thread bottom leg under and extend, creating a twist with hip opening."),
]


def _slugify(name: str) -> str:
    """Convert pose name to URL-friendly slug."""
    import re
    slug = name.lower().strip()
    slug = re.sub(r"[''']", "", slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def seed_database():
    """Insert all poses into the database."""
    from database import init_db, db_is_seeded, get_connection

    init_db()
    if db_is_seeded():
        print("Database already seeded.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    pose_count = 0

    for english, sanskrit, category, diff, hold, bilateral, tags, desc in POSES:
        slug = _slugify(english)

        # Avoid duplicate slugs
        existing = cursor.execute("SELECT id FROM poses WHERE slug=?", (slug,)).fetchone()
        if existing:
            slug = slug + "-v"

        cursor.execute("""
            INSERT INTO poses (english_name, sanskrit_name, slug, description,
                               category, difficulty, is_bilateral, default_hold_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (english, sanskrit, slug, desc, category, diff, int(bilateral), hold))

        pose_id = cursor.lastrowid
        pose_count += 1

        # Insert tags
        for tag in tags:
            cursor.execute(
                "INSERT OR IGNORE INTO pose_tags (pose_id, tag) VALUES (?, ?)",
                (pose_id, tag)
            )

        # If bilateral, create left/right variants
        if bilateral:
            for side in ["Left", "Right"]:
                side_name = f"{english} ({side})"
                side_slug = f"{_slugify(english)}-{side.lower()}"
                side_sanskrit = f"{sanskrit} ({side})" if sanskrit else None

                cursor.execute("""
                    INSERT INTO poses (english_name, sanskrit_name, slug, description,
                                       category, difficulty, is_bilateral, default_hold_seconds,
                                       parent_pose_id)
                    VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
                """, (side_name, side_sanskrit, side_slug,
                      f"{desc} — {side.lower()} side.",
                      category, diff, hold, pose_id))

                child_id = cursor.lastrowid
                pose_count += 1

                for tag in tags:
                    cursor.execute(
                        "INSERT OR IGNORE INTO pose_tags (pose_id, tag) VALUES (?, ?)",
                        (child_id, tag)
                    )

    conn.commit()
    conn.close()
    print(f"✅ Seeded {pose_count} poses (including bilateral L/R variants).")


if __name__ == "__main__":
    seed_database()
