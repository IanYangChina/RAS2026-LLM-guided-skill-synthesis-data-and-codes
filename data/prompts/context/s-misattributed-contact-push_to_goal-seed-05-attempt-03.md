## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.2620 | 0.63 | ✅ accepted |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ❌ rejected |
| 1 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.63 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

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
| `object` | offset from object initial position (0.5366003508494456, 0.03695289476837925, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
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

## Current Skill (Q=0.262) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - -0.275
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: none
  parameters:
    approach_offset:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_time:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 6
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: contact_check
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, -0.275], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=replace_offset_projection, sign=negative}
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=replace_offset_projection, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.262
- **task_score** (E): 0.627
- **fitness_score**: 0.562  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.3122 |
| push_1 | 1.00 | 1.00 | 0.2339 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.572, 0.048, 0.003) | (0.519, 0.022, 0.025)→(0.539, 0.016, 0.029) | 0.173→0.171 | 1.00 / 3.667 | 8.306 | 104.265 |
| push_1 | push | 1.00 / time_limit | (0.572, 0.048, 0.003)→(0.501, -0.174, 0.007) | (0.539, 0.016, 0.029)→(0.474, -0.108, 0.026) | 0.171→0.066 | 1.00 / 4.000 | 212.969 | 398.259 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.724
- goal_progress: 0.813
- terminal_score: 0.813
- phase_score: 0.645
- phase_breakdown.push_to_goal_score: 0.817
- phase_breakdown.pre_contact_score: 0.242

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.712
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.813
- **Median Q (composite search score)**: 0.301
- **K-run variance**: 0.0200
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_time
- **Final σ (mean)**: 0.363


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15686,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset":0.05923,"approach_1.approach_speed":0.11909,"approach_1.approach_tolerance":0.02359,"push_1.push_distance":0.3292,"push_1.push_speed":0.15049,"push_1.push_time":3.27669},"optimized_scores":{"best_composite_score":0.41219,"best_fitness_score":0.71219,"best_task_score":0.8132},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":104.0,"contact_point_centroid":[0.58641,0.04266,0.04633],"force_p95":284.37608,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":442.36321,"mean_force":194.11184,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.59633,0.06612,0.00309]},{"body_a":"attachment","body_b":"push_box","contact_count":469.0,"contact_point_centroid":[0.56378,0.04893,0.0453],"force_p95":294.58641,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":336.92258,"mean_force":225.28707,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.56108,0.05373,0.04444]},{"body_a":"attachment","body_b":"world","contact_count":40.0,"contact_point_centroid":[0.6066,0.06284,-0.0007],"force_p95":269.74381,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.36883,"mean_force":72.67353,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.59507,0.06574,7e-05]},{"body_a":"world","body_b":"push_box","contact_count":3033.0,"contact_point_centroid":[0.54692,0.03882,-0.00045],"force_p95":164.32944,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":231.36165,"mean_force":41.89807,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53125,0.03503,0.11757]},{"body_a":"push_box","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.55608,-0.04931,0.04905],"force_p95":99.57498,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.96108,"mean_force":61.55427,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55682,-0.03374,0.00653]},{"body_a":"world","body_b":"push_box","contact_count":1675.0,"contact_point_centroid":[0.54557,-0.05505,-0.00021],"force_p95":82.41836,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.66261,"mean_force":42.06387,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56071,-0.02418,0.00657]},{"body_a":"attachment","body_b":"push_box","contact_count":707.0,"contact_point_centroid":[0.54995,-0.04734,0.00852],"force_p95":45.38293,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.93222,"mean_force":29.05006,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55547,-0.0375,0.00694]},{"body_a":"attachment","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.60764,0.06622,-0.0],"force_p95":4.12802,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.12802,"mean_force":4.12802,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.59596,0.06815,0.00193]}],"total_contact_groups":8},"final_pose_error":0.32854,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46918,-0.16729,0.02919],"final_tcp_position":[0.50724,-0.15361,0.0053],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":442.36321,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5637,0.0342,0.02804],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19493,"object_to_goal_dist_start":0.1905,"object_z_max":0.03534,"peak_contact_force":24.42612,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3383.0,"raw_peak_contact_force":120.96108,"subtask_id":"pre_contact","tcp_end":[0.59596,0.06815,0.00193],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05362,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46918,-0.16729,0.02919],"object_pos_start":[0.5637,0.0342,0.02804],"object_to_goal_dist_end":0.03559,"object_to_goal_dist_start":0.19493,"object_z_max":0.0309,"peak_contact_force":194.98572,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3646.0,"raw_peak_contact_force":442.36321,"subtask_id":"push_to_goal","tcp_end":[0.50724,-0.15361,0.0053],"tcp_start":[0.59596,0.06815,0.00193],"tcp_to_object_dist_end":0.04698,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93407,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset":0.02337,"approach_1.approach_speed":0.13986,"approach_1.approach_tolerance":0.01848,"push_1.push_distance":0.16467,"push_1.push_speed":0.14086,"push_1.push_time":4.70407},"optimized_scores":{"best_composite_score":0.3012,"best_fitness_score":0.6012,"best_task_score":0.68101},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":142.0,"contact_point_centroid":[0.56471,0.00442,-0.00038],"force_p95":336.28031,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.77629,"mean_force":247.32304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55321,0.00449,0.00266]},{"body_a":"push_box","body_b":"link7","contact_count":159.0,"contact_point_centroid":[0.56201,-0.03156,0.04547],"force_p95":129.79639,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":340.61516,"mean_force":88.0242,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55418,0.00455,0.00374]},{"body_a":"world","body_b":"push_box","contact_count":2998.0,"contact_point_centroid":[0.51267,-0.01921,-0.00034],"force_p95":182.10874,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":315.40037,"mean_force":31.20519,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51086,0.00192,0.12853]},{"body_a":"attachment","body_b":"push_box","contact_count":353.0,"contact_point_centroid":[0.53272,-0.00153,0.04447],"force_p95":273.9716,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":293.09905,"mean_force":222.09376,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53083,0.00366,0.04338]},{"body_a":"attachment","body_b":"world","contact_count":66.0,"contact_point_centroid":[0.5278,-0.1164,-0.0],"force_p95":85.14264,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.70814,"mean_force":60.44641,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51672,-0.11666,0.00458]},{"body_a":"world","body_b":"push_box","contact_count":2330.0,"contact_point_centroid":[0.48601,-0.10854,-0.00013],"force_p95":63.63061,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.0927,"mean_force":13.46973,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51532,-0.12266,0.00514]},{"body_a":"push_box","body_b":"link7","contact_count":584.0,"contact_point_centroid":[0.53499,-0.06553,0.05011],"force_p95":78.38407,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.2949,"mean_force":48.63481,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5381,-0.04928,0.00512]},{"body_a":"attachment","body_b":"push_box","contact_count":290.0,"contact_point_centroid":[0.52396,-0.07221,0.00902],"force_p95":25.80297,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.10969,"mean_force":13.28487,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53315,-0.0659,0.00539]}],"total_contact_groups":8},"final_pose_error":0.1051,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46484,-0.12726,0.02499],"final_tcp_position":[0.48956,-0.20882,0.00622],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":423.77629,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52473,-0.03355,0.03198],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.11925,"object_to_goal_dist_start":0.13127,"object_z_max":0.03773,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3270.0,"raw_peak_contact_force":92.70814,"subtask_id":"pre_contact","tcp_end":[0.55341,0.00449,0.00374],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05539,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46484,-0.12726,0.02499],"object_pos_start":[0.52473,-0.03355,0.03198],"object_to_goal_dist_end":0.04187,"object_to_goal_dist_start":0.11925,"object_z_max":0.03199,"peak_contact_force":306.98578,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3652.0,"raw_peak_contact_force":423.77629,"subtask_id":"push_to_goal","tcp_end":[0.48956,-0.20882,0.00622],"tcp_start":[0.55341,0.00449,0.00374],"tcp_to_object_dist_end":0.08726,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22807,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset":0.06,"approach_1.approach_speed":0.02056,"approach_1.approach_tolerance":0.02264,"push_1.push_distance":0.15876,"push_1.push_speed":0.15073,"push_1.push_time":9.99986},"optimized_scores":{"best_composite_score":0.07263,"best_fitness_score":0.37263,"best_task_score":0.38672},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":474.0,"contact_point_centroid":[0.5439,0.05396,0.04511],"force_p95":285.69033,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":328.63795,"mean_force":222.43292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54192,0.0589,0.044]},{"body_a":"push_box","body_b":"link7","contact_count":85.0,"contact_point_centroid":[0.56027,0.05088,0.04768],"force_p95":198.98066,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":328.11193,"mean_force":146.71151,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.56823,0.07148,0.00401]},{"body_a":"world","body_b":"push_box","contact_count":3009.0,"contact_point_centroid":[0.52374,0.04934,-0.00041],"force_p95":142.92189,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":266.03465,"mean_force":39.56702,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51792,0.0377,0.1218]},{"body_a":"attachment","body_b":"world","contact_count":65.0,"contact_point_centroid":[0.5777,0.0704,-0.00051],"force_p95":208.54846,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.47978,"mean_force":75.7988,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.56603,0.07181,0.0014]},{"body_a":"push_box","body_b":"link7","contact_count":538.0,"contact_point_centroid":[0.53969,0.01764,0.05115],"force_p95":88.03677,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.1268,"mean_force":53.70897,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55321,0.01894,0.00553]},{"body_a":"world","body_b":"push_box","contact_count":2656.0,"contact_point_centroid":[0.50155,-0.01919,-0.00011],"force_p95":47.21377,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.59881,"mean_force":12.00945,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53119,-0.06342,0.00676]},{"body_a":"attachment","body_b":"push_box","contact_count":261.0,"contact_point_centroid":[0.54061,0.00316,0.00851],"force_p95":30.57244,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.55783,"mean_force":16.26385,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55053,0.00887,0.0058]},{"body_a":"attachment","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.57771,0.0707,-3e-05],"force_p95":14.61337,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":16.23707,"mean_force":5.41236,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56606,0.07185,0.00258]}],"total_contact_groups":8},"final_pose_error":0.15001,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4882,-0.029,0.02499],"final_tcp_position":[0.50672,-0.16069,0.01024],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":328.63795,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52932,0.04771,0.02653],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19987,"object_to_goal_dist_start":0.19823,"object_z_max":0.03636,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3458.0,"raw_peak_contact_force":99.1268,"subtask_id":"pre_contact","tcp_end":[0.56601,0.07185,0.00254],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05006,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4882,-0.029,0.02499],"object_pos_start":[0.52932,0.04771,0.02653],"object_to_goal_dist_end":0.12157,"object_to_goal_dist_start":0.19987,"object_z_max":0.03102,"peak_contact_force":136.93593,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3633.0,"raw_peak_contact_force":328.63795,"subtask_id":"push_to_goal","tcp_end":[0.50672,-0.16069,0.01024],"tcp_start":[0.56601,0.07185,0.00254],"tcp_to_object_dist_end":0.1338,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```