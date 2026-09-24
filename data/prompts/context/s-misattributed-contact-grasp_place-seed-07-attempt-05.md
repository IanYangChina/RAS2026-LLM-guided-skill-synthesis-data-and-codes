## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.5617 | 0.15 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | time_limit | 11 | -0.4617 | 0.17 | ❌ rejected |
| 3 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 2 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.562) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: -0.562
- **task_score** (E): 0.145
- **fitness_score**: 0.168  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 0.00 | 1.00 | 0.1213 |
| descend_to_grasp | 0.00 | 1.00 | 0.0528 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.33 | 1.00 | 0.0749 |
| transport_to_goal | 0.00 | 1.00 | 0.1008 |
| descend_to_place | 0.00 | 1.00 | 0.0242 |
| release_object | 1.00 | 1.00 | 0.0242 |
| retract_final | 1.00 | 1.00 | 0.0823 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.447, 0.011, 0.195) | (0.511, 0.022, 0.030)→(0.471, 0.024, 0.016) | 0.271→0.296 | 1.00 / 6.333 | 212.210 | 983.676 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.447, 0.011, 0.195)→(0.472, 0.009, 0.158) | (0.471, 0.024, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 10.667 | 237986.657 | 246.614 |
| grasp_object | grasp | 1.00 / step_budget | (0.472, 0.009, 0.158)→(0.472, 0.009, 0.158) | (0.471, 0.024, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 8.333 | 91094.638 | 244.356 |
| lift_object | lift | 0.33 / step_budget | (0.472, 0.009, 0.158)→(0.470, 0.018, 0.231) | (0.471, 0.025, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 9.000 | 182003.862 | 208.588 |
| transport_to_goal | approach | 0.00 / step_budget | (0.470, 0.018, 0.231)→(0.509, 0.065, 0.297) | (0.471, 0.024, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 9.000 | 188.211 | 205.031 |
| descend_to_place | descend | 0.00 / step_budget | (0.509, 0.065, 0.297)→(0.522, 0.085, 0.297) | (0.471, 0.024, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 5.000 | 159.279 | 170.720 |
| release_object | release | 1.00 / step_budget | (0.522, 0.085, 0.297)→(0.523, 0.085, 0.321) | (0.471, 0.024, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 4.000 | 0.123 | 189.173 |
| retract_final | retract | 1.00 / step_budget | (0.523, 0.085, 0.321)→(0.527, 0.084, 0.403) | (0.471, 0.024, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 5.000 | 313.349 | 1453.286 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.204
- phase_score: 0.140
- phase_breakdown.lift_object_score: 0.305
- phase_breakdown.place_object_score: 0.050
- phase_breakdown.grasp_approach_score: 0.155
- phase_breakdown.pre_grasp_score: 0.141
- phase_breakdown.approach_goal_score: 0.046
- grasp_place_fitness: 0.194

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.194
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.204
- **Median Q (composite search score)**: -0.574
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.311


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":89.0,"average_failure_rate":0.37083,"average_mean_iterations":77.03333,"average_solve_count":240.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.08968,"approach_above_object.pre_grasp_z":0.11473,"descend_to_grasp.descend_speed":0.09198,"descend_to_grasp.grasp_z":0.05352,"descend_to_place.place_speed":0.02859,"descend_to_place.place_z":0.09191,"lift_object.lift_speed":0.04642,"lift_object.lift_z":0.24884,"retract_final.retract_speed":0.05542,"transport_to_goal.transport_speed":0.07155,"transport_to_goal.transport_z":0.19085},"optimized_scores":{"best_composite_score":-0.53578,"best_fitness_score":0.19422,"best_task_score":0.20398},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.6331,0.00773,-0.00047],"force_p95":208.25855,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1435.78459,"mean_force":204.23044,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.40351,0.00744,0.14172]},{"body_a":"world","body_b":"link6","contact_count":986.0,"contact_point_centroid":[0.6563,0.02365,-0.00021],"force_p95":372.31301,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":915.03644,"mean_force":298.0052,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45459,0.02205,0.18982]},{"body_a":"link5","body_b":"hand","contact_count":358.0,"contact_point_centroid":[0.54463,0.0043,0.23441],"force_p95":311.95554,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.70826,"mean_force":270.55551,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51402,0.08329,0.26112]},{"body_a":"link5","body_b":"hand","contact_count":8.0,"contact_point_centroid":[0.5385,0.01115,0.21355],"force_p95":275.33534,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.38153,"mean_force":252.83734,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52332,0.09069,0.26673]},{"body_a":"world","body_b":"link6","contact_count":542.0,"contact_point_centroid":[0.70359,0.02415,-0.00012],"force_p95":67.72034,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.40732,"mean_force":65.76729,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47396,0.02956,0.16421]},{"body_a":"link5","body_b":"hand","contact_count":15.0,"contact_point_centroid":[0.544,0.0165,0.23479],"force_p95":224.64879,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.95628,"mean_force":138.724,"phase_index":7.0,"phase_name":"retract_final","phase_type":"retract","tcp_position_centroid":[0.52342,0.09415,0.28644]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.70362,0.02405,-0.0001],"force_p95":223.71102,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.03403,"mean_force":174.15401,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47397,0.02959,0.16422]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53909,0.01393,0.21255],"force_p95":206.96983,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":211.82785,"mean_force":178.26268,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52283,0.09311,0.26552]},{"body_a":"grasp_target","body_b":"link7","contact_count":244.0,"contact_point_centroid":[0.49447,0.0232,0.04148],"force_p95":2.7007,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.50047,"mean_force":0.59539,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.3891,0.00374,0.10139]},{"body_a":"left_finger","body_b":"link5","contact_count":39.0,"contact_point_centroid":[0.47062,-0.01654,0.17406],"force_p95":4.81111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.94406,"mean_force":2.24789,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47331,0.02925,0.16454]},{"body_a":"grasp_target","body_b":"hand","contact_count":217.0,"contact_point_centroid":[0.48714,0.02452,0.05443],"force_p95":2.33141,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.78672,"mean_force":0.5599,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38851,0.00363,0.09839]},{"body_a":"world","body_b":"grasp_target","contact_count":3417.0,"contact_point_centroid":[0.47967,0.04738,-0.00255],"force_p95":0.29983,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41066,"mean_force":0.1742,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.41783,0.00735,0.15455]},{"body_a":"left_finger","body_b":"link5","contact_count":113.0,"contact_point_centroid":[0.47141,-0.01526,0.17452],"force_p95":1.62679,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.39362,"mean_force":0.6874,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47399,0.02945,0.16438]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46914,0.04955,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45476,0.02213,0.18959]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.46914,0.04955,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47397,0.02956,0.16422]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46914,0.04955,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47017,0.03853,0.20187]}],"total_contact_groups":26},"final_pose_error":0.01177,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.46914,0.04955,0.01602],"final_tcp_position":[0.52392,0.09395,0.37417],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.12089,"phases":[{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46914,0.04955,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.23846,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":262.27084,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5025.0,"raw_peak_contact_force":915.03644,"subtask_id":"pre_grasp","tcp_end":[0.4254,0.01412,0.18702],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18002,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46914,0.04955,0.01602],"object_pos_start":[0.46914,0.04955,0.01602],"object_to_goal_dist_end":0.23846,"object_to_goal_dist_start":0.23846,"object_z_max":0.01602,"peak_contact_force":273004.12089,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3637.0,"raw_peak_contact_force":242.40732,"subtask_id":"grasp_approach","tcp_end":[0.47387,0.02933,0.1643],"tcp_start":[0.4254,0.01412,0.18702],"tcp_to_object_dist_end":0.14973,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.46914,0.04955,0.01602],"object_pos_start":[0.46914,0.04955,0.01602],"object_to_goal_dist_end":0.23846,"object_to_goal_dist_start":0.23846,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8324.0,"raw_peak_contact_force":225.03403,"tcp_end":[0.47396,0.02959,0.16418],"tcp_start":[0.47396,0.02959,0.16418],"tcp_to_object_dist_end":0.14958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46914,0.04955,0.01602],"object_pos_start":[0.46914,0.04955,0.01602],"object_to_goal_dist_end":0.23846,"object_to_goal_dist_start":0.23846,"object_z_max":0.01602,"peak_contact_force":272989.59029,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8707.0,"raw_peak_contact_force":335.70826,"subtask_id":"lift_object","tcp_end":[0.46846,0.04589,0.24055],"tcp_start":[0.47396,0.02959,0.16418],"tcp_to_object_dist_end":0.22456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46914,0.04955,0.01602],"object_pos_start":[0.46914,0.04955,0.01602],"object_to_goal_dist_end":0.23846,"object_to_goal_dist_start":0.23846,"object_z_max":0.01602,"peak_contact_force":245.16648,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":73.0,"raw_peak_contact_force":282.38153,"subtask_id":"approach_goal","tcp_end":[0.52328,0.09046,0.26698],"tcp_start":[0.46846,0.04589,0.24055],"tcp_to_object_dist_end":0.25997,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.46914,0.04955,0.01602],"object_pos_start":[0.46914,0.04955,0.01602],"object_to_goal_dist_end":0.23846,"object_to_goal_dist_start":0.23846,"object_z_max":0.01602,"peak_contact_force":211.82785,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1219.0,"raw_peak_contact_force":211.82785,"subtask_id":"place_object","tcp_end":[0.52321,0.09177,0.26534],"tcp_start":[0.52328,0.09046,0.26698],"tcp_to_object_dist_end":0.25859,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46914,0.04955,0.01602],"object_pos_start":[0.46914,0.04955,0.01602],"object_to_goal_dist_end":0.23846,"object_to_goal_dist_start":0.23846,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4015.0,"raw_peak_contact_force":226.95628,"tcp_end":[0.52335,0.09391,0.28593],"tcp_start":[0.52321,0.09177,0.26534],"tcp_to_object_dist_end":0.27885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46914,0.04955,0.01602],"object_pos_start":[0.46914,0.04955,0.01602],"object_to_goal_dist_end":0.23846,"object_to_goal_dist_start":0.23846,"object_z_max":0.01602,"peak_contact_force":201.04607,"phase_name":"retract_final","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4785.0,"raw_peak_contact_force":1435.78459,"tcp_end":[0.52392,0.09395,0.37417],"tcp_start":[0.52335,0.09391,0.28593],"tcp_to_object_dist_end":0.36503,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":39.0,"average_failure_rate":0.19307,"average_mean_iterations":42.24752,"average_solve_count":202.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.19452,"approach_above_object.pre_grasp_z":0.07385,"descend_to_grasp.descend_speed":0.07063,"descend_to_grasp.grasp_z":0.05187,"descend_to_place.place_speed":0.05801,"descend_to_place.place_z":0.05065,"lift_object.lift_speed":0.03368,"lift_object.lift_z":0.34992,"retract_final.retract_speed":0.09672,"transport_to_goal.transport_speed":0.06748,"transport_to_goal.transport_z":0.25791},"optimized_scores":{"best_composite_score":-0.57536,"best_fitness_score":0.15464,"best_task_score":0.12519},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":878.0,"contact_point_centroid":[0.63671,0.02047,-0.00042],"force_p95":416.89328,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1509.61183,"mean_force":247.88537,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.41936,0.01688,0.15792]},{"body_a":"world","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.66109,0.04801,-0.00027],"force_p95":373.75103,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":794.60725,"mean_force":291.52779,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46086,0.04189,0.18638]},{"body_a":"link5","body_b":"hand","contact_count":380.0,"contact_point_centroid":[0.52993,0.0699,0.2373],"force_p95":275.58109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.43896,"mean_force":235.35272,"phase_index":7.0,"phase_name":"retract_final","phase_type":"retract","tcp_position_centroid":[0.51229,0.14258,0.3009]},{"body_a":"link5","body_b":"hand","contact_count":216.0,"contact_point_centroid":[0.5401,0.05641,0.23163],"force_p95":320.42319,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":332.59011,"mean_force":305.39632,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51088,0.14251,0.25307]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52982,0.0097,-0.0036],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.06318,"mean_force":13.35057,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37887,0.00506,0.04647]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53831,0.07399,0.21784],"force_p95":296.61865,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.20934,"mean_force":258.62418,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52128,0.15417,0.26098]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.68725,0.03912,-9e-05],"force_p95":191.87476,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.21644,"mean_force":96.31255,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46389,0.04725,0.16436]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68716,0.03906,-0.00013],"force_p95":74.51971,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.86582,"mean_force":68.01672,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4639,0.0471,0.16441]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.45954,0.04566,0.03972],"force_p95":3.6355,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.97641,"mean_force":1.70096,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38905,0.00509,0.04969]},{"body_a":"world","body_b":"grasp_target","contact_count":3921.0,"contact_point_centroid":[0.4473,0.05056,-0.00213],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44602,"mean_force":0.13826,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.42905,0.01569,0.16494]},{"body_a":"grasp_target","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.49074,0.02909,0.00934],"force_p95":0.74634,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.79241,"mean_force":0.35277,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37867,0.00508,0.04842]},{"body_a":"left_finger","body_b":"link5","contact_count":23.0,"contact_point_centroid":[0.50998,0.11191,0.2648],"force_p95":0.14127,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.18729,"mean_force":0.07648,"phase_index":7.0,"phase_name":"retract_final","phase_type":"retract","tcp_position_centroid":[0.52033,0.15295,0.28211]},{"body_a":"left_finger","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.51132,0.11354,0.26433],"force_p95":0.1436,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.14361,"mean_force":0.14321,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5219,0.15458,0.28052]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44238,0.05081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46086,0.04189,0.18636]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44238,0.05081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4639,0.0471,0.16441]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44238,0.05081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45726,0.0478,0.20468]}],"total_contact_groups":25},"final_pose_error":0.03227,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44238,0.05081,0.01602],"final_tcp_position":[0.53522,0.15169,0.35204],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273021.87222,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44238,0.05081,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31169,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":254.14031,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4996.0,"raw_peak_contact_force":794.60725,"subtask_id":"pre_grasp","tcp_end":[0.45662,0.03857,0.20263],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18755,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44238,0.05081,0.01602],"object_pos_start":[0.44238,0.05081,0.01602],"object_to_goal_dist_end":0.31169,"object_to_goal_dist_start":0.31169,"object_z_max":0.01602,"peak_contact_force":273004.12084,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3525.0,"raw_peak_contact_force":97.86582,"subtask_id":"grasp_approach","tcp_end":[0.4639,0.04685,0.16491],"tcp_start":[0.45662,0.03857,0.20263],"tcp_to_object_dist_end":0.15049,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44238,0.05081,0.01602],"object_pos_start":[0.44238,0.05081,0.01602],"object_to_goal_dist_end":0.31169,"object_to_goal_dist_start":0.31169,"object_z_max":0.01602,"peak_contact_force":272980.36406,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8240.0,"raw_peak_contact_force":204.21644,"tcp_end":[0.46389,0.04711,0.1643],"tcp_start":[0.46389,0.04711,0.1643],"tcp_to_object_dist_end":0.14988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44238,0.05081,0.01602],"object_pos_start":[0.44238,0.05081,0.01602],"object_to_goal_dist_end":0.31169,"object_to_goal_dist_start":0.31169,"object_z_max":0.01602,"peak_contact_force":273021.87222,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8305.0,"raw_peak_contact_force":0.12263,"subtask_id":"lift_object","tcp_end":[0.45302,0.04853,0.24596],"tcp_start":[0.46389,0.04711,0.1643],"tcp_to_object_dist_end":0.2302,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44238,0.05081,0.01602],"object_pos_start":[0.44238,0.05081,0.01602],"object_to_goal_dist_end":0.31169,"object_to_goal_dist_start":0.31169,"object_z_max":0.01602,"peak_contact_force":319.34474,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4832.0,"raw_peak_contact_force":332.59011,"subtask_id":"approach_goal","tcp_end":[0.48114,0.09749,0.25788],"tcp_start":[0.45302,0.04853,0.24596],"tcp_to_object_dist_end":0.24935,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.44238,0.05081,0.01602],"object_pos_start":[0.44238,0.05081,0.01602],"object_to_goal_dist_end":0.31169,"object_to_goal_dist_start":0.31169,"object_z_max":0.01602,"peak_contact_force":265.8866,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1230.0,"raw_peak_contact_force":300.20934,"subtask_id":"place_object","tcp_end":[0.52095,0.15447,0.25832],"tcp_start":[0.48114,0.09749,0.25788],"tcp_to_object_dist_end":0.275,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44238,0.05081,0.01602],"object_pos_start":[0.44238,0.05081,0.01602],"object_to_goal_dist_end":0.31169,"object_to_goal_dist_start":0.31169,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2695.0,"raw_peak_contact_force":340.43896,"tcp_end":[0.5219,0.15459,0.28129],"tcp_start":[0.52095,0.15447,0.25832],"tcp_to_object_dist_end":0.29574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.44238,0.05081,0.01602],"object_pos_start":[0.44238,0.05081,0.01602],"object_to_goal_dist_end":0.31169,"object_to_goal_dist_start":0.31169,"object_z_max":0.01602,"peak_contact_force":383.20474,"phase_name":"retract_final","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4888.0,"raw_peak_contact_force":1509.61183,"tcp_end":[0.53522,0.15169,0.35204],"tcp_start":[0.5219,0.15459,0.28129],"tcp_to_object_dist_end":0.36291,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":185.0,"average_failure_rate":0.59486,"average_mean_iterations":122.28939,"average_solve_count":311.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.13411,"approach_above_object.pre_grasp_z":0.16601,"descend_to_grasp.descend_speed":0.0877,"descend_to_grasp.grasp_z":0.04428,"descend_to_place.place_speed":0.05274,"descend_to_place.place_z":0.02566,"lift_object.lift_speed":0.04278,"lift_object.lift_z":0.26954,"retract_final.retract_speed":0.06932,"transport_to_goal.transport_speed":0.08202,"transport_to_goal.transport_z":0.1601},"optimized_scores":{"best_composite_score":-0.57388,"best_fitness_score":0.15612,"best_task_score":0.10611},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":881.0,"contact_point_centroid":[0.63991,-0.00541,-0.00044],"force_p95":409.96523,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1414.463,"mean_force":238.3123,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.42446,-0.00769,0.16318]},{"body_a":"world","body_b":"link6","contact_count":210.0,"contact_point_centroid":[0.68941,-0.00528,-0.00019],"force_p95":594.85201,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1241.38451,"mean_force":350.68482,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47263,-0.02542,0.17416]},{"body_a":"world","body_b":"link5","contact_count":390.0,"contact_point_centroid":[0.64412,0.11142,-0.00031],"force_p95":390.27583,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":922.91038,"mean_force":313.89172,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4908,-0.04141,0.16849]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53317,0.00101,-0.00317],"force_p95":23.0121,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":460.24195,"mean_force":23.0121,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37972,-0.00273,0.05046]},{"body_a":"link5","body_b":"hand","contact_count":571.0,"contact_point_centroid":[0.51713,0.06568,0.12692],"force_p95":199.91804,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":406.97737,"mean_force":103.35187,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48275,-0.02906,0.17627]},{"body_a":"world","body_b":"link5","contact_count":546.0,"contact_point_centroid":[0.6419,0.09877,-2e-05],"force_p95":18.01142,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":399.56951,"mean_force":15.29154,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47736,-0.05001,0.14454]},{"body_a":"link5","body_b":"hand","contact_count":703.0,"contact_point_centroid":[0.54451,0.00383,0.2367],"force_p95":303.51398,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.81853,"mean_force":285.37484,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48494,-0.04308,0.18611]},{"body_a":"link5","body_b":"hand","contact_count":15.0,"contact_point_centroid":[0.5484,0.00534,0.25778],"force_p95":288.3848,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.93454,"mean_force":193.46796,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49009,-0.04046,0.20657]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.71405,-0.00687,-5e-05],"force_p95":136.0228,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.73554,"mean_force":76.27493,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47738,-0.05005,0.14482]},{"body_a":"world","body_b":"link6","contact_count":545.0,"contact_point_centroid":[0.71261,-0.00382,-0.0001],"force_p95":67.0285,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.0443,"mean_force":51.58627,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47736,-0.05001,0.14454]},{"body_a":"world","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.64192,0.09871,-2e-05],"force_p95":48.01687,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.49044,"mean_force":14.12261,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47736,-0.05009,0.1445]},{"body_a":"grasp_target","body_b":"link7","contact_count":187.0,"contact_point_centroid":[0.51405,-0.02221,0.03637],"force_p95":3.28095,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.73281,"mean_force":0.6706,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39402,-0.00306,0.09958]},{"body_a":"grasp_target","body_b":"link6","contact_count":110.0,"contact_point_centroid":[0.54145,-0.02572,0.029],"force_p95":0.90129,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.00421,"mean_force":0.47738,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38842,-0.0029,0.09155]},{"body_a":"grasp_target","body_b":"hand","contact_count":112.0,"contact_point_centroid":[0.49513,-0.02819,0.04855],"force_p95":2.37667,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.10222,"mean_force":0.92973,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39009,-0.00284,0.08459]},{"body_a":"world","body_b":"grasp_target","contact_count":3697.0,"contact_point_centroid":[0.50789,-0.02719,-0.00219],"force_p95":0.2453,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.67234,"mean_force":0.1504,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.43623,-0.00735,0.17309]},{"body_a":"grasp_target","body_b":"hand","contact_count":87.0,"contact_point_centroid":[0.53498,-0.03953,0.03669],"force_p95":0.28581,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.59535,"mean_force":0.07923,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47772,-0.04906,0.14892]}],"total_contact_groups":30},"final_pose_error":0.01347,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50195,-0.02691,0.01602],"final_tcp_position":[0.52332,0.00674,0.48225],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50264,-0.02858,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33754,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":120.2184,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3646.0,"raw_peak_contact_force":1241.38451,"subtask_id":"pre_grasp","tcp_end":[0.46023,-0.01843,0.1965],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18567,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":617.0,"n_steps_budget":1000.0,"object_pos_end":[0.50246,-0.02805,0.01631],"object_pos_start":[0.50264,-0.02858,0.01602],"object_to_goal_dist_end":0.33703,"object_to_goal_dist_start":0.33754,"object_z_max":0.01624,"peak_contact_force":167951.73011,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4622.0,"raw_peak_contact_force":399.56951,"subtask_id":"grasp_approach","tcp_end":[0.47726,-0.04998,0.14412],"tcp_start":[0.46023,-0.01843,0.1965],"tcp_to_object_dist_end":0.13211,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50208,-0.02693,0.01594],"object_pos_start":[0.50246,-0.02805,0.01631],"object_to_goal_dist_end":0.33651,"object_to_goal_dist_start":0.33703,"object_z_max":0.01651,"peak_contact_force":303.42611,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9110.0,"raw_peak_contact_force":303.81853,"tcp_end":[0.47735,-0.05007,0.14447],"tcp_start":[0.47735,-0.05006,0.14447],"tcp_to_object_dist_end":0.13292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50195,-0.02691,0.01602],"object_pos_start":[0.50202,-0.02684,0.01595],"object_to_goal_dist_end":0.33649,"object_to_goal_dist_start":0.33645,"object_z_max":0.01622,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5773.0,"raw_peak_contact_force":289.93454,"subtask_id":"lift_object","tcp_end":[0.48984,-0.04085,0.20665],"tcp_start":[0.47735,-0.05007,0.14447],"tcp_to_object_dist_end":0.19153,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.50195,-0.02691,0.01602],"object_pos_start":[0.50195,-0.02691,0.01602],"object_to_goal_dist_end":0.33649,"object_to_goal_dist_start":0.33649,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.5214,0.00712,0.36584],"tcp_start":[0.48984,-0.04085,0.20665],"tcp_to_object_dist_end":0.35201,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50195,-0.02691,0.01602],"object_pos_start":[0.50195,-0.02691,0.01602],"object_to_goal_dist_end":0.33649,"object_to_goal_dist_start":0.33649,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.52131,0.00746,0.3669],"tcp_start":[0.5214,0.00712,0.36584],"tcp_to_object_dist_end":0.35309,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50195,-0.02691,0.01602],"object_pos_start":[0.50195,-0.02691,0.01602],"object_to_goal_dist_end":0.33649,"object_to_goal_dist_start":0.33649,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52259,0.00786,0.39565],"tcp_start":[0.52131,0.00746,0.3669],"tcp_to_object_dist_end":0.38178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":754.0,"n_steps_budget":900.0,"object_pos_end":[0.50195,-0.02691,0.01602],"object_pos_start":[0.50195,-0.02691,0.01602],"object_to_goal_dist_end":0.33649,"object_to_goal_dist_start":0.33649,"object_z_max":0.01602,"peak_contact_force":355.79485,"phase_name":"retract_final","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5007.0,"raw_peak_contact_force":1414.463,"tcp_end":[0.52332,0.00674,0.48225],"tcp_start":[0.52259,0.00786,0.39565],"tcp_to_object_dist_end":0.46793,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```