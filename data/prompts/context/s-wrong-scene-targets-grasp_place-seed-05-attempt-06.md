## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.1719 | 0.22 | ❌ rejected |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.530500292374538, 0.030794078973649372, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.530500292374538, 0.030794078973649372, 0.03]
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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
| `object` | offset from object initial position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=-0.172) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_angle:
      type: angle
      range:
      - 0.1
      - 1.2
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: release_2
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
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
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.172
- **task_score** (E): 0.218
- **fitness_score**: 0.200  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.208
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1384 |
| descend_grasp | 1.00 | 1.00 | 0.0004 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.0911 |
| transport_goal | 0.00 | 1.00 | 0.1000 |
| descend_place | 0.67 | 1.00 | 0.0003 |
| release | 1.00 | 1.00 | 0.0252 |
| retract | 1.00 | 1.00 | 0.0878 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.464, 0.009, 0.170) | (0.516, 0.018, 0.030)→(0.503, 0.025, 0.023) | 0.234→0.238 | 1.00 / 5.000 | 91300.585 | 1350.497 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.464, 0.009, 0.170)→(0.465, 0.008, 0.170) | (0.503, 0.025, 0.023)→(0.503, 0.025, 0.023) | 0.238→0.238 | 1.00 / 4.667 | 45443.764 | 938.381 |
| grasp | grasp | 1.00 / step_budget | (0.464, 0.008, 0.168)→(0.464, 0.008, 0.168) | (0.503, 0.025, 0.023)→(0.503, 0.025, 0.023) | 0.238→0.238 | 1.00 / 9.333 | 91046.339 | 317.874 |
| lift | lift | 1.00 / step_budget | (0.464, 0.008, 0.168)→(0.463, 0.008, 0.259) | (0.503, 0.025, 0.023)→(0.503, 0.025, 0.023) | 0.238→0.238 | 1.00 / 9.000 | 182003.569 | 178.669 |
| transport_goal | approach | 0.00 / step_budget | (0.463, 0.008, 0.259)→(0.515, 0.083, 0.233) | (0.503, 0.025, 0.023)→(0.503, 0.025, 0.023) | 0.238→0.238 | 1.00 / 9.000 | 197.180 | 421.490 |
| descend_place | descend | 0.67 / force_exceeded | (0.515, 0.083, 0.233)→(0.516, 0.083, 0.233) | (0.503, 0.025, 0.023)→(0.503, 0.025, 0.023) | 0.238→0.238 | 1.00 / 9.000 | 159.254 | 159.254 |
| release | release | 1.00 / step_budget | (0.516, 0.083, 0.233)→(0.517, 0.087, 0.258) | (0.503, 0.025, 0.023)→(0.503, 0.025, 0.023) | 0.238→0.238 | 1.00 / 6.000 | 168.447 | 226.994 |
| retract | retract | 1.00 / step_budget | (0.517, 0.087, 0.258)→(0.507, 0.010, 0.293) | (0.503, 0.025, 0.023)→(0.503, 0.025, 0.023) | 0.238→0.238 | 1.00 / 6.667 | 230.221 | 203.289 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.287
- phase_score: 0.049
- phase_breakdown.place_goal_score: 0.000
- phase_breakdown.pre_grasp_score: 0.163
- grasp_place_fitness: 0.229

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.229
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.287
- **Median Q (composite search score)**: -0.117
- **K-run variance**: 0.0080
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.244


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.60153,0.17858,0.10809]},{"name":"goal","value":[0.5305,0.03079,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":19.0,"average_failure_rate":0.20652,"average_mean_iterations":46.17391,"average_solve_count":92.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.15446,"descend_grasp.descend_force_threshold":5.44834,"descend_grasp.descend_speed":0.03055,"descend_place.place_force_threshold":5.40266,"lift.lift_height":0.08983,"lift.lift_speed":0.11066,"retract.retract_speed":0.16914,"transport_goal.transport_speed":0.15745},"optimized_scores":{"best_composite_score":-0.10078,"best_fitness_score":0.22922,"best_task_score":0.28671},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":865.0,"contact_point_centroid":[0.64302,0.00989,-0.00043],"force_p95":450.15016,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1309.88332,"mean_force":242.15088,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42503,0.00792,0.15948]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53286,0.00687,-0.0032],"force_p95":390.08791,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1241.19401,"mean_force":77.68009,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38084,0.00244,0.0487]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.6765,0.02203,-0.00043],"force_p95":1154.96728,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1154.96728,"mean_force":1154.96728,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46443,0.01957,0.17122]},{"body_a":"world","body_b":"link6","contact_count":37.0,"contact_point_centroid":[0.65426,0.0118,-0.00057],"force_p95":479.72754,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":489.76754,"mean_force":340.67937,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.50195,0.09111,0.19345]},{"body_a":"world","body_b":"link6","contact_count":543.0,"contact_point_centroid":[0.67852,0.02166,-0.00013],"force_p95":74.36399,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":424.063,"mean_force":71.93317,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46441,0.01935,0.16929]},{"body_a":"link5","body_b":"hand","contact_count":167.0,"contact_point_centroid":[0.52942,0.0005,0.17745],"force_p95":370.76109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":394.16574,"mean_force":309.98826,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.49901,0.07431,0.2066]},{"body_a":"link5","body_b":"hand","contact_count":542.0,"contact_point_centroid":[0.53257,-0.01183,0.21506],"force_p95":306.3229,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.24512,"mean_force":272.07011,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50891,0.06103,0.2538]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.52434,0.02008,0.15881],"force_p95":252.33895,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.93193,"mean_force":232.79829,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.50665,0.09376,0.20266]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.52262,0.01819,0.15218],"force_p95":231.88367,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.88367,"mean_force":231.88367,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50515,0.09264,0.19497]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.67863,0.02159,-9e-05],"force_p95":176.50584,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":177.32488,"mean_force":124.56702,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46439,0.01932,0.16918]},{"body_a":"world","body_b":"link6","contact_count":78.0,"contact_point_centroid":[0.65522,0.01067,-0.0001],"force_p95":67.97472,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":168.46971,"mean_force":54.46085,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.50614,0.09195,0.19608]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.65513,0.01035,-0.0001],"force_p95":116.61537,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.61537,"mean_force":116.61537,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50515,0.09264,0.19497]},{"body_a":"grasp_target","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.50272,0.01897,0.03617],"force_p95":3.77579,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.84429,"mean_force":0.84001,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39155,0.00275,0.08543]},{"body_a":"grasp_target","body_b":"hand","contact_count":116.0,"contact_point_centroid":[0.50204,0.04015,0.05412],"force_p95":2.16767,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.20204,"mean_force":0.88507,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39076,0.00272,0.08321]},{"body_a":"world","body_b":"grasp_target","contact_count":3649.0,"contact_point_centroid":[0.50451,0.0476,-0.00226],"force_p95":0.38832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.38502,"mean_force":0.15897,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4379,0.00788,0.17079]},{"body_a":"grasp_target","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.5404,0.03198,0.02262],"force_p95":0.84052,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.95014,"mean_force":0.50655,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38694,0.00268,0.08315]}],"total_contact_groups":30},"final_pose_error":0.01672,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49936,0.0513,0.01602],"final_tcp_position":[0.50453,0.01226,0.28957],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273005.44797,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49936,0.0513,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18739,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":781.19219,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4860.0,"raw_peak_contact_force":1309.88332,"subtask_id":"pre_grasp","tcp_end":[0.46443,0.01957,0.17122],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16222,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49936,0.0513,0.01602],"object_pos_start":[0.49936,0.0513,0.01602],"object_to_goal_dist_end":0.18739,"object_to_goal_dist_start":0.18739,"object_z_max":0.01602,"peak_contact_force":1154.96728,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":1154.96728,"tcp_end":[0.46451,0.01954,0.17081],"tcp_start":[0.46443,0.01957,0.17122],"tcp_to_object_dist_end":0.16182,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49936,0.0513,0.01602],"object_pos_start":[0.49936,0.0513,0.01602],"object_to_goal_dist_end":0.18739,"object_to_goal_dist_start":0.18739,"object_z_max":0.01602,"peak_contact_force":67.33728,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3523.0,"raw_peak_contact_force":424.063,"tcp_end":[0.4644,0.01934,0.16917],"tcp_start":[0.4644,0.01934,0.16917],"tcp_to_object_dist_end":0.16031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49936,0.0513,0.01602],"object_pos_start":[0.49936,0.0513,0.01602],"object_to_goal_dist_end":0.18739,"object_to_goal_dist_start":0.18739,"object_z_max":0.01602,"peak_contact_force":273005.44797,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4265.0,"raw_peak_contact_force":177.32488,"tcp_end":[0.46301,0.01921,0.24663],"tcp_start":[0.4644,0.01934,0.16917],"tcp_to_object_dist_end":0.23565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.49936,0.0513,0.01602],"object_pos_start":[0.49936,0.0513,0.01602],"object_to_goal_dist_end":0.18739,"object_to_goal_dist_start":0.18739,"object_z_max":0.01602,"peak_contact_force":293.83922,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4545.0,"raw_peak_contact_force":489.76754,"subtask_id":"place_goal","tcp_end":[0.50515,0.09264,0.19497],"tcp_start":[0.46301,0.01921,0.24663],"tcp_to_object_dist_end":0.18376,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49936,0.0513,0.01602],"object_pos_start":[0.49936,0.0513,0.01602],"object_to_goal_dist_end":0.18739,"object_to_goal_dist_start":0.18739,"object_z_max":0.01602,"peak_contact_force":231.88367,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":231.88367,"tcp_end":[0.50536,0.09245,0.1952],"tcp_start":[0.50515,0.09264,0.19497],"tcp_to_object_dist_end":0.18394,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49936,0.0513,0.01602],"object_pos_start":[0.49936,0.0513,0.01602],"object_to_goal_dist_end":0.18739,"object_to_goal_dist_start":0.18739,"object_z_max":0.01602,"peak_contact_force":251.58157,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1404.0,"raw_peak_contact_force":254.93193,"tcp_end":[0.50871,0.09832,0.22345],"tcp_start":[0.50536,0.09245,0.1952],"tcp_to_object_dist_end":0.2129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49936,0.0513,0.01602],"object_pos_start":[0.49936,0.0513,0.01602],"object_to_goal_dist_end":0.18739,"object_to_goal_dist_start":0.18739,"object_z_max":0.01602,"peak_contact_force":310.12158,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4300.0,"raw_peak_contact_force":310.24512,"tcp_end":[0.50453,0.01226,0.28957],"tcp_start":[0.50871,0.09832,0.22345],"tcp_to_object_dist_end":0.27637,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":32.0,"average_failure_rate":0.24242,"average_mean_iterations":52.88636,"average_solve_count":132.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.19835,"descend_grasp.descend_force_threshold":5.46361,"descend_grasp.descend_speed":0.02905,"descend_place.place_force_threshold":5.04312,"lift.lift_height":0.12724,"lift.lift_speed":0.05911,"retract.retract_speed":0.13741,"transport_goal.transport_speed":0.15685},"optimized_scores":{"best_composite_score":-0.2985,"best_fitness_score":0.1565,"best_task_score":0.12343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":869.0,"contact_point_centroid":[0.64687,-0.00439,-0.0004],"force_p95":479.51232,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1409.17931,"mean_force":242.26518,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42679,-0.00576,0.15456]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67733,0.00406,-3e-05],"force_p95":883.90076,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":883.90076,"mean_force":883.90076,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46494,-0.02841,0.16856]},{"body_a":"world","body_b":"link6","contact_count":549.0,"contact_point_centroid":[0.67877,0.00254,-0.00012],"force_p95":71.45674,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.01076,"mean_force":69.45598,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46503,-0.02967,0.1667]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.5333,0.00127,-0.00342],"force_p95":42.421,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.54515,"mean_force":15.7252,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38216,-0.00199,0.04635]},{"body_a":"link5","body_b":"hand","contact_count":236.0,"contact_point_centroid":[0.54076,0.10272,0.21732],"force_p95":230.73034,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.87418,"mean_force":133.05518,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.50592,-0.00556,0.21911]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.67879,0.00261,-0.0001],"force_p95":151.49918,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.71291,"mean_force":100.71115,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46499,-0.02965,0.16665]},{"body_a":"world","body_b":"link5","contact_count":44.0,"contact_point_centroid":[0.64791,0.07719,-0.00016],"force_p95":94.58222,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.65709,"mean_force":43.97938,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53004,0.07468,0.26682]},{"body_a":"grasp_target","body_b":"link7","contact_count":311.0,"contact_point_centroid":[0.50204,-0.0219,0.0424],"force_p95":1.30613,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.01802,"mean_force":0.55077,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40036,-0.00257,0.11087]},{"body_a":"grasp_target","body_b":"hand","contact_count":259.0,"contact_point_centroid":[0.49348,-0.02929,0.05514],"force_p95":2.84922,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.41223,"mean_force":0.64756,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39789,-0.00235,0.1022]},{"body_a":"world","body_b":"grasp_target","contact_count":3259.0,"contact_point_centroid":[0.49681,-0.01703,-0.00243],"force_p95":0.2753,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43366,"mean_force":0.16906,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44274,-0.00603,0.16944]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50009,-0.01655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46494,-0.02841,0.16856]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50009,-0.01655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46503,-0.02967,0.16671]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50009,-0.01655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46345,-0.02959,0.21416]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50009,-0.01655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.50609,0.01495,0.24623]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.50009,-0.01655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52994,0.07506,0.27083]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50009,-0.01655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5302,0.07452,0.27369]}],"total_contact_groups":22},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50009,-0.01655,0.02602],"final_tcp_position":[0.50952,0.0027,0.29882],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273005.13705,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50009,-0.01655,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31381,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":272729.1982,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4721.0,"raw_peak_contact_force":1409.17931,"subtask_id":"pre_grasp","tcp_end":[0.46494,-0.02841,0.16856],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14729,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50009,-0.01655,0.02602],"object_pos_start":[0.50009,-0.01655,0.02602],"object_to_goal_dist_end":0.31381,"object_to_goal_dist_start":0.31381,"object_z_max":0.02602,"peak_contact_force":134400.05046,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":883.90076,"tcp_end":[0.46502,-0.02867,0.16816],"tcp_start":[0.46494,-0.02841,0.16856],"tcp_to_object_dist_end":0.14691,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50009,-0.01655,0.02602],"object_pos_start":[0.50009,-0.01655,0.02602],"object_to_goal_dist_end":0.31381,"object_to_goal_dist_start":0.31381,"object_z_max":0.02602,"peak_contact_force":273004.12078,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3540.0,"raw_peak_contact_force":325.01076,"tcp_end":[0.46501,-0.02968,0.16659],"tcp_start":[0.46501,-0.02968,0.16659],"tcp_to_object_dist_end":0.14548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50009,-0.01655,0.02602],"object_pos_start":[0.50009,-0.01655,0.02602],"object_to_goal_dist_end":0.31381,"object_to_goal_dist_start":0.31381,"object_z_max":0.02602,"peak_contact_force":273005.13705,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8415.0,"raw_peak_contact_force":161.71291,"tcp_end":[0.46378,-0.02974,0.26237],"tcp_start":[0.46501,-0.02968,0.16659],"tcp_to_object_dist_end":0.23949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50009,-0.01655,0.02602],"object_pos_start":[0.50009,-0.01655,0.02602],"object_to_goal_dist_end":0.31381,"object_to_goal_dist_start":0.31381,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8670.0,"raw_peak_contact_force":269.87418,"subtask_id":"place_goal","tcp_end":[0.52986,0.07517,0.27087],"tcp_start":[0.46378,-0.02974,0.26237],"tcp_to_object_dist_end":0.26315,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50009,-0.01655,0.02602],"object_pos_start":[0.50009,-0.01655,0.02602],"object_to_goal_dist_end":0.31381,"object_to_goal_dist_start":0.31381,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53011,0.07486,0.27073],"tcp_start":[0.52986,0.07517,0.27087],"tcp_to_object_dist_end":0.26294,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50009,-0.01655,0.02602],"object_pos_start":[0.50009,-0.01655,0.02602],"object_to_goal_dist_end":0.31381,"object_to_goal_dist_start":0.31381,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1069.0,"raw_peak_contact_force":128.65709,"tcp_end":[0.53039,0.07425,0.29361],"tcp_start":[0.53011,0.07486,0.27073],"tcp_to_object_dist_end":0.2842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":600.0,"object_pos_end":[0.50009,-0.01655,0.02602],"object_pos_start":[0.50009,-0.01655,0.02602],"object_to_goal_dist_end":0.31381,"object_to_goal_dist_start":0.31381,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1392.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50952,0.0027,0.29882],"tcp_start":[0.53039,0.07425,0.29361],"tcp_to_object_dist_end":0.27364,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":17.0,"average_failure_rate":0.16505,"average_mean_iterations":37.23301,"average_solve_count":103.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.18798,"descend_grasp.descend_force_threshold":8.83629,"descend_grasp.descend_speed":0.0657,"descend_place.place_force_threshold":7.22537,"lift.lift_height":0.12118,"lift.lift_speed":0.06086,"retract.retract_speed":0.12304,"transport_goal.transport_speed":0.2297},"optimized_scores":{"best_composite_score":-0.11656,"best_fitness_score":0.21344,"best_task_score":0.24293},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":829.0,"contact_point_centroid":[0.64663,0.01477,-0.00041],"force_p95":498.95414,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1332.42863,"mean_force":251.79326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42664,0.01311,0.15491]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53392,0.00853,-0.0032],"force_p95":279.24409,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1326.31949,"mean_force":71.15612,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38287,0.00407,0.04699]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67741,0.0345,-0.00019],"force_p95":776.27354,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":776.27354,"mean_force":776.27354,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46406,0.03437,0.17013]},{"body_a":"link5","body_b":"hand","contact_count":105.0,"contact_point_centroid":[0.53987,0.00554,0.2114],"force_p95":462.09482,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":504.82957,"mean_force":365.26646,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.50659,0.0801,0.23426]},{"body_a":"link5","body_b":"hand","contact_count":517.0,"contact_point_centroid":[0.53875,-0.01686,0.23483],"force_p95":296.38716,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.49888,"mean_force":272.21661,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51168,0.05603,0.27232]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.5342,0.011,0.1906],"force_p95":264.40189,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.39289,"mean_force":235.84128,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.51133,0.08337,0.23542]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.53411,0.00888,0.18892],"force_p95":245.75578,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":245.75578,"mean_force":245.75578,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51123,0.08148,0.23325]},{"body_a":"world","body_b":"link6","contact_count":543.0,"contact_point_centroid":[0.67874,0.03344,-0.00013],"force_p95":75.04142,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.54777,"mean_force":69.51714,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46397,0.03377,0.16846]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.67888,0.03336,-0.0001],"force_p95":192.6194,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.97028,"mean_force":121.71566,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46395,0.03375,0.16829]},{"body_a":"grasp_target","body_b":"link7","contact_count":259.0,"contact_point_centroid":[0.50262,0.02387,0.04202],"force_p95":1.34159,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.82969,"mean_force":0.59139,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39917,0.00547,0.10529]},{"body_a":"grasp_target","body_b":"hand","contact_count":219.0,"contact_point_centroid":[0.49529,0.02439,0.05537],"force_p95":2.71835,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.74499,"mean_force":0.60246,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39696,0.00502,0.09774]},{"body_a":"world","body_b":"grasp_target","contact_count":3099.0,"contact_point_centroid":[0.50685,0.04168,-0.0026],"force_p95":0.2894,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.54195,"mean_force":0.17819,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44314,0.01361,0.17039]},{"body_a":"left_finger","body_b":"link5","contact_count":1449.0,"contact_point_centroid":[0.50293,0.0184,0.26365],"force_p95":0.72078,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.72939,"mean_force":0.29015,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51157,0.05416,0.27336]},{"body_a":"left_finger","body_b":"link5","contact_count":75.0,"contact_point_centroid":[0.50322,0.04825,0.23647],"force_p95":0.66812,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.71296,"mean_force":0.52763,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.51228,0.08575,0.24743]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.51063,0.04133,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46406,0.03437,0.17013]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.51063,0.04133,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46398,0.03377,0.16847]}],"total_contact_groups":26},"final_pose_error":0.01904,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51063,0.04133,0.02602],"final_tcp_position":[0.50665,0.01582,0.29176],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1332.42863,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.51063,0.04133,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":391.36492,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4429.0,"raw_peak_contact_force":1332.42863,"subtask_id":"pre_grasp","tcp_end":[0.46406,0.03437,0.17013],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15161,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51063,0.04133,0.02602],"object_pos_start":[0.51063,0.04133,0.02602],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21225,"object_z_max":0.02602,"peak_contact_force":776.27354,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":776.27354,"tcp_end":[0.4641,0.03435,0.16987],"tcp_start":[0.46406,0.03437,0.17013],"tcp_to_object_dist_end":0.15135,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51063,0.04133,0.02602],"object_pos_start":[0.51063,0.04133,0.02602],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21225,"object_z_max":0.02602,"peak_contact_force":67.55748,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3522.0,"raw_peak_contact_force":204.54777,"tcp_end":[0.46397,0.03376,0.16836],"tcp_start":[0.46397,0.03376,0.16836],"tcp_to_object_dist_end":0.14998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51063,0.04133,0.02602],"object_pos_start":[0.51063,0.04133,0.02602],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21225,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8346.0,"raw_peak_contact_force":196.97028,"tcp_end":[0.46276,0.03363,0.26832],"tcp_start":[0.46397,0.03376,0.16836],"tcp_to_object_dist_end":0.24711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.51063,0.04133,0.02602],"object_pos_start":[0.51063,0.04133,0.02602],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21225,"object_z_max":0.02602,"peak_contact_force":297.57816,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3171.0,"raw_peak_contact_force":504.82957,"subtask_id":"place_goal","tcp_end":[0.51123,0.08148,0.23325],"tcp_start":[0.46276,0.03363,0.26832],"tcp_to_object_dist_end":0.21109,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51063,0.04133,0.02602],"object_pos_start":[0.51063,0.04133,0.02602],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21225,"object_z_max":0.02602,"peak_contact_force":245.75578,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":245.75578,"tcp_end":[0.51135,0.08147,0.23319],"tcp_start":[0.51123,0.08148,0.23325],"tcp_to_object_dist_end":0.21103,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51063,0.04133,0.02602],"object_pos_start":[0.51063,0.04133,0.02602],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21225,"object_z_max":0.02602,"peak_contact_force":253.63726,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1301.0,"raw_peak_contact_force":297.39289,"tcp_end":[0.51296,0.08718,0.25611],"tcp_start":[0.51135,0.08147,0.23319],"tcp_to_object_dist_end":0.23463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":517.0,"n_steps_budget":600.0,"object_pos_end":[0.51063,0.04133,0.02602],"object_pos_start":[0.51063,0.04133,0.02602],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21225,"object_z_max":0.02602,"peak_contact_force":299.39894,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4034.0,"raw_peak_contact_force":299.49888,"tcp_end":[0.50665,0.01582,0.29176],"tcp_start":[0.51296,0.08718,0.25611],"tcp_to_object_dist_end":0.26699,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```