## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1148 | 0.24 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2590 | 0.33 | ✅ accepted |
| 2 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |
| 1 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | final destination targets |
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

## Current Skill (Q=0.115) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_grasp
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
- id: lift_clear
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: transport_approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  subtask_id: reach_goal
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: release
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=repeat
- **transport_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_depth: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.115
- **task_score** (E): 0.237
- **fitness_score**: 0.595  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_grasp | 1.00 | 1.00 | 0.2170 |
| descend_to_grasp | 1.00 | 1.00 | 0.0515 |
| grasp | 1.00 | 0.67 | 0.0122 |
| lift_clear | 1.00 | 1.00 | 0.1203 |
| transport_approach | 0.67 | 1.00 | 0.2351 |
| place_descend | 1.00 | 1.00 | 0.1481 |
| release | 1.00 | 1.00 | 0.0203 |
| retract | 1.00 | 1.00 | 0.0375 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 9.684 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.505, 0.002, 0.036) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.140 | 0.205 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.002, 0.036)→(0.497, 0.002, 0.028) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 0.67 / 14.333 | 0.098 | 0.682 |
| lift_clear | lift | 1.00 / step_budget | (0.497, 0.002, 0.028)→(0.493, 0.002, 0.148) | (0.511, 0.002, 0.026)→(0.508, 0.004, 0.125) | 0.246→0.217 | 1.00 / 8.333 | 91003.795 | 1.656 |
| transport_approach | approach | 0.67 / step_budget | (0.493, 0.002, 0.148)→(0.600, 0.148, 0.293) | (0.508, 0.004, 0.125)→(0.505, 0.046, 0.016) | 0.217→0.221 | 1.00 / 8.333 | 91002.296 | 0.123 |
| place_descend | descend | 1.00 / step_budget | (0.600, 0.148, 0.293)→(0.620, 0.177, 0.149) | (0.505, 0.046, 0.016)→(0.505, 0.046, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.620, 0.177, 0.149)→(0.614, 0.175, 0.169) | (0.505, 0.046, 0.016)→(0.505, 0.046, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.614, 0.175, 0.169)→(0.610, 0.174, 0.206) | (0.505, 0.046, 0.016)→(0.505, 0.046, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.327
- phase_score: 0.603
- phase_breakdown.reach_grasp_score: 0.368
- phase_breakdown.reach_goal_score: 0.704
- grasp_place_fitness: 0.639

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.639
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.327
- **Median Q (composite search score)**: 0.099
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.308


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0229,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.36654,"descend_to_grasp.descend_depth":0.00609,"lift_clear.lift_height":0.10373,"place_descend.place_depth":0.00444,"transport_approach.arc_height":0.05028,"transport_approach.transport_speed":0.37668},"optimized_scores":{"best_composite_score":0.09896,"best_fitness_score":0.57896,"best_task_score":0.20322},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2610.0,"contact_point_centroid":[0.49499,0.03719,-0.00237],"force_p95":0.12577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61236,"mean_force":0.13879,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.53713,0.09519,0.23865]},{"body_a":"world","body_b":"grasp_target","contact_count":122.0,"contact_point_centroid":[0.45559,-0.0249,-0.00113],"force_p95":0.42945,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56411,"mean_force":0.06861,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44528,-0.02542,0.03542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2634.0,"contact_point_centroid":[0.45842,0.00887,0.14932],"force_p95":0.15882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2989,"mean_force":0.09853,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.45266,-0.00958,0.1499]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8850.0,"contact_point_centroid":[0.44503,-0.00636,0.07667],"force_p95":0.10421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29418,"mean_force":0.06572,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44287,-0.02532,0.07454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9520.0,"contact_point_centroid":[0.44504,-0.04421,0.07516],"force_p95":0.10123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28949,"mean_force":0.06201,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44287,-0.02532,0.07358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2681.0,"contact_point_centroid":[0.45785,-0.0288,0.14822],"force_p95":0.16171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28666,"mean_force":0.09714,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.45206,-0.01039,0.14874]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02618,-0.00207],"force_p95":0.14391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20372,"mean_force":0.12833,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44769,-0.02551,0.03465]},{"body_a":"world","body_b":"grasp_target","contact_count":2156.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13209,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.47801,-0.01202,0.19471]},{"body_a":"world","body_b":"grasp_target","contact_count":688.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45469,-0.02503,0.06526]},{"body_a":"world","body_b":"grasp_target","contact_count":1704.0,"contact_point_centroid":[0.49499,0.0372,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60898,0.18602,0.18957]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49499,0.0372,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61776,0.20147,0.12234]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.49499,0.0372,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61245,0.19953,0.15922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4817.0,"contact_point_centroid":[0.44667,-0.00625,0.03605],"force_p95":0.06873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1081,"mean_force":0.04491,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44662,-0.02547,0.03364]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5183.0,"contact_point_centroid":[0.44651,-0.0447,0.03555],"force_p95":0.06766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0765,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44662,-0.02547,0.03364]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2548.0,"contact_point_centroid":[0.54284,0.10179,0.24484],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01045,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54249,0.10179,0.24248]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.62125,0.20265,0.1209],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62083,0.20263,0.11896]}],"total_contact_groups":17},"final_pose_error":0.01343,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.49499,0.0372,0.01602],"final_tcp_position":[0.61222,0.19943,0.17881],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273011.13963,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":688.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.45719,-0.02443,0.08962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1407,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11800.0,"raw_peak_contact_force":0.20372,"subtask_id":"reach_grasp","tcp_end":[0.45415,-0.02574,0.04085],"tcp_start":[0.45719,-0.02443,0.08962],"tcp_to_object_dist_end":0.01549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02559,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.11198,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18492.0,"raw_peak_contact_force":0.56411,"tcp_end":[0.44659,-0.02547,0.03361],"tcp_start":[0.45415,-0.02574,0.04085],"tcp_to_object_dist_end":0.01425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.45777,-0.02525,0.11005],"object_pos_start":[0.45847,-0.02559,0.02574],"object_to_goal_dist_end":0.29022,"object_to_goal_dist_start":0.30322,"object_z_max":0.10994,"peak_contact_force":273011.13963,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10473.0,"raw_peak_contact_force":1.61236,"tcp_end":[0.44278,-0.0253,0.12634],"tcp_start":[0.44659,-0.02547,0.03361],"tcp_to_object_dist_end":0.02215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49499,0.0372,0.01602],"object_pos_start":[0.45777,-0.02525,0.11005],"object_to_goal_dist_end":0.23902,"object_to_goal_dist_start":0.29022,"object_z_max":0.15525,"peak_contact_force":0.12263,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3535.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59764,0.1702,0.25938],"tcp_start":[0.44278,-0.0253,0.12634],"tcp_to_object_dist_end":0.29572,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.49499,0.0372,0.01602],"object_pos_start":[0.49499,0.0372,0.01602],"object_to_goal_dist_end":0.23902,"object_to_goal_dist_start":0.23902,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62279,0.20314,0.12281],"tcp_start":[0.59764,0.1702,0.25938],"tcp_to_object_dist_end":0.2351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49499,0.0372,0.01602],"object_pos_start":[0.49499,0.0372,0.01602],"object_to_goal_dist_end":0.23902,"object_to_goal_dist_start":0.23902,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6159,0.20077,0.14165],"tcp_start":[0.62279,0.20314,0.12281],"tcp_to_object_dist_end":0.23907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49499,0.0372,0.01602],"object_pos_start":[0.49499,0.0372,0.01602],"object_to_goal_dist_end":0.23902,"object_to_goal_dist_start":0.23902,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2156.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.61222,0.19943,0.17881],"tcp_start":[0.6159,0.20077,0.14165],"tcp_to_object_dist_end":0.25799,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97973,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.25389,"descend_to_grasp.descend_depth":0.00457,"lift_clear.lift_height":0.16751,"place_descend.place_depth":0.00382,"transport_approach.arc_height":0.11009,"transport_approach.transport_speed":0.36841},"optimized_scores":{"best_composite_score":0.08618,"best_fitness_score":0.56618,"best_task_score":0.18043},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3749.0,"contact_point_centroid":[0.52277,0.01764,-0.00224],"force_p95":0.12491,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73471,"mean_force":0.13515,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54652,0.03023,0.30917]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.54112,0.00073,-0.00111],"force_p95":0.47954,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67474,"mean_force":0.09378,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52756,0.00082,0.02978]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11072.0,"contact_point_centroid":[0.5289,-0.01784,0.09366],"force_p95":0.13777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33569,"mean_force":0.08382,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52494,0.00078,0.09287]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11797.0,"contact_point_centroid":[0.52894,0.01931,0.09446],"force_p95":0.13419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31806,"mean_force":0.08094,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52498,0.00078,0.09388]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.13215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15923,"mean_force":0.12535,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53045,0.00088,0.02956]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.5174,0.00049,0.19249]},{"body_a":"world","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53635,0.00098,0.06226]},{"body_a":"world","body_b":"grasp_target","contact_count":1728.0,"contact_point_centroid":[0.52267,0.01769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62985,0.13784,0.27939]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52267,0.01769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6376,0.15274,0.20046]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.52267,0.01769,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63356,0.15151,0.23699]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53045,-0.01835,0.0308],"force_p95":0.07612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11479,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5292,0.00086,0.02813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53036,0.01993,0.02992],"force_p95":0.06818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09157,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5292,0.00086,0.02813]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3778.0,"contact_point_centroid":[0.54851,0.0322,0.31774],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0155,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54812,0.0322,0.31548]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1841.0,"contact_point_centroid":[0.63031,0.13788,0.28152],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01046,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62987,0.13786,0.27926]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.64034,0.15353,0.19944],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01025,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64002,0.15351,0.19724]}],"total_contact_groups":15},"final_pose_error":0.0134,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.52267,0.01769,0.01602],"final_tcp_position":[0.63347,0.15145,0.25655],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273006.64341,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":28.8057,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":660.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.53706,0.00099,0.08675],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":165.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1301,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15923,"subtask_id":"reach_grasp","tcp_end":[0.53781,0.00101,0.03815],"tcp_start":[0.53706,0.00099,0.08675],"tcp_to_object_dist_end":0.01376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.0,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":23009.0,"raw_peak_contact_force":0.67474,"tcp_end":[0.52917,0.00085,0.02809],"tcp_start":[0.53781,0.00101,0.03815],"tcp_to_object_dist_end":0.01516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.53447,0.00784,0.14213],"object_pos_start":[0.54417,0.00073,0.02588],"object_to_goal_dist_end":0.19436,"object_to_goal_dist_start":0.25053,"object_z_max":0.15429,"peak_contact_force":0.12263,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7527.0,"raw_peak_contact_force":1.73471,"tcp_end":[0.52546,0.00079,0.18291],"tcp_start":[0.52917,0.00085,0.02809],"tcp_to_object_dist_end":0.04236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52267,0.01769,0.01602],"object_pos_start":[0.53447,0.00784,0.14213],"object_to_goal_dist_end":0.25686,"object_to_goal_dist_start":0.19436,"object_z_max":0.14213,"peak_contact_force":273006.64341,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3569.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.61958,0.12312,0.3587],"tcp_start":[0.52546,0.00079,0.18291],"tcp_to_object_dist_end":0.3714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":432.0,"n_steps_budget":1000.0,"object_pos_end":[0.52267,0.01769,0.01602],"object_pos_start":[0.52267,0.01769,0.01602],"object_to_goal_dist_end":0.25686,"object_to_goal_dist_start":0.25686,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.64162,0.15378,0.20132],"tcp_start":[0.61958,0.12312,0.3587],"tcp_to_object_dist_end":0.25886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52267,0.01769,0.01602],"object_pos_start":[0.52267,0.01769,0.01602],"object_to_goal_dist_end":0.25686,"object_to_goal_dist_start":0.25686,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63621,0.15229,0.21964],"tcp_start":[0.64162,0.15378,0.20132],"tcp_to_object_dist_end":0.2692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.52267,0.01769,0.01602],"object_pos_start":[0.52267,0.01769,0.01602],"object_to_goal_dist_end":0.25686,"object_to_goal_dist_start":0.25686,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63347,0.15145,0.25655],"tcp_start":[0.63621,0.15229,0.21964],"tcp_to_object_dist_end":0.29669,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92701,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.37486,"descend_to_grasp.descend_depth":-0.00324,"lift_clear.lift_height":0.12532,"place_descend.place_depth":0.00943,"transport_approach.arc_height":0.17586,"transport_approach.transport_speed":0.26146},"optimized_scores":{"best_composite_score":0.15921,"best_fitness_score":0.63921,"best_task_score":0.32675},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2728.0,"contact_point_centroid":[0.49849,0.08153,-0.00245],"force_p95":0.22427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62084,"mean_force":0.15019,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54487,0.08856,0.24379]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.52727,0.02851,-0.0012],"force_p95":0.58959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80598,"mean_force":0.10901,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.5142,0.02934,0.02271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10441.0,"contact_point_centroid":[0.51504,0.04797,0.07156],"force_p95":0.1115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32911,"mean_force":0.07239,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51159,0.02917,0.07028]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10385.0,"contact_point_centroid":[0.51474,0.01041,0.07381],"force_p95":0.11302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32659,"mean_force":0.07199,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51156,0.02917,0.07267]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.51181,0.04677,0.14517],"force_p95":0.19215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31306,"mean_force":0.11343,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50884,0.02889,0.14936]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03041,-0.00212],"force_p95":0.15887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2506,"mean_force":0.13249,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51711,0.02954,0.02227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1555.0,"contact_point_centroid":[0.5119,0.01061,0.14277],"force_p95":0.18204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24201,"mean_force":0.10944,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.5089,0.02873,0.14672]},{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.51098,0.01417,0.19292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4045.0,"contact_point_centroid":[0.51699,0.01027,0.02365],"force_p95":0.08049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13507,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51588,0.02946,0.02091]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52311,0.02926,0.05861]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.49869,0.08321,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58757,0.16156,0.19176]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49869,0.08321,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59031,0.17288,0.12445]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.49869,0.08321,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58504,0.17119,0.16257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.51687,0.04863,0.02269],"force_p95":0.07276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09129,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51588,0.02946,0.02092]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2969.0,"contact_point_centroid":[0.54476,0.08778,0.24588],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54439,0.08777,0.24354]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1698.0,"contact_point_centroid":[0.58797,0.16157,0.19403],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01054,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58756,0.16155,0.19184]}],"total_contact_groups":17},"final_pose_error":0.01259,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49869,0.08321,0.01602],"final_tcp_position":[0.5848,0.1711,0.18225],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.62084,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":756.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52411,0.02864,0.08733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15024,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10841.0,"raw_peak_contact_force":0.2506,"subtask_id":"reach_grasp","tcp_end":[0.52441,0.03003,0.03044],"tcp_start":[0.52411,0.02864,0.08733],"tcp_to_object_dist_end":0.00757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53035,0.02936,0.02561],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18129,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20973.0,"raw_peak_contact_force":0.80598,"tcp_end":[0.51585,0.02945,0.02088],"tcp_start":[0.52441,0.03003,0.03044],"tcp_to_object_dist_end":0.01525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.53131,0.02929,0.12239],"object_pos_start":[0.53035,0.02936,0.02561],"object_to_goal_dist_end":0.1656,"object_to_goal_dist_start":0.18476,"object_z_max":0.12233,"peak_contact_force":0.12263,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9080.0,"raw_peak_contact_force":1.62084,"tcp_end":[0.51175,0.02919,0.13401],"tcp_start":[0.51585,0.02945,0.02088],"tcp_to_object_dist_end":0.02276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49869,0.08321,0.01602],"object_pos_start":[0.53131,0.02929,0.12239],"object_to_goal_dist_end":0.16778,"object_to_goal_dist_start":0.1656,"object_z_max":0.14066,"peak_contact_force":0.12263,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3306.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.58199,0.15002,0.26094],"tcp_start":[0.51175,0.02919,0.13401],"tcp_to_object_dist_end":0.26719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.49869,0.08321,0.01602],"object_pos_start":[0.49869,0.08321,0.01602],"object_to_goal_dist_end":0.16778,"object_to_goal_dist_start":0.16778,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5953,0.17435,0.12396],"tcp_start":[0.58199,0.15002,0.26094],"tcp_to_object_dist_end":0.17115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49869,0.08321,0.01602],"object_pos_start":[0.49869,0.08321,0.01602],"object_to_goal_dist_end":0.16778,"object_to_goal_dist_start":0.16778,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58848,0.17227,0.14423],"tcp_start":[0.5953,0.17435,0.12396],"tcp_to_object_dist_end":0.18009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49869,0.08321,0.01602],"object_pos_start":[0.49869,0.08321,0.01602],"object_to_goal_dist_end":0.16778,"object_to_goal_dist_start":0.16778,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.5848,0.1711,0.18225],"tcp_start":[0.58848,0.17227,0.14423],"tcp_to_object_dist_end":0.20681,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```