## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1969 | 0.28 | ❌ rejected |
| 2 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2195 | 0.23 | ❌ rejected |
| 1 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2558 | 0.29 | ✅ accepted |
| 0 | descend → grasp → approach → descend → release | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.0443 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.197) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place
  weight: 0.5
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_grasp
- id: grasp_1
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
  guards:
  - id: bilateral_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_1
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_clear
- id: transport_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_2
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.197
- **task_score** (E): 0.276
- **fitness_score**: 0.617  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2662 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1064 |
| transport_1 | 0.67 | 0.67 | 0.2679 |
| descend_2 | 1.00 | 1.00 | 0.1074 |
| release_1 | 1.00 | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.038) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.511, -0.001, 0.033)→(0.511, -0.001, 0.033) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 45.333 | 0.166 | 0.248 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.033)→(0.507, -0.001, 0.139) | (0.522, -0.001, 0.025)→(0.522, -0.001, 0.125) | 0.290→0.240 | 1.00 / 25.333 | 83.126 | 0.625 |
| transport_1 | approach | 0.67 / step_budget | (0.507, -0.001, 0.139)→(0.595, 0.179, 0.316) | (0.522, -0.001, 0.125)→(0.606, 0.175, 0.069) | 0.240→0.166 | 0.67 / 2.000 | 0.843 | 1.612 |
| descend_2 | descend | 1.00 / step_budget | (0.595, 0.179, 0.316)→(0.603, 0.202, 0.213) | (0.606, 0.175, 0.069)→(0.609, 0.176, 0.016) | 0.166→0.195 | 1.00 / 8.667 | 91002.289 | 1.617 |
| release_1 | release | 1.00 / step_budget | (0.603, 0.202, 0.213)→(0.598, 0.201, 0.232) | (0.609, 0.176, 0.016)→(0.609, 0.176, 0.016) | 0.195→0.195 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.327
- phase_score: 0.707
- phase_breakdown.pre_grasp_score: 0.457
- phase_breakdown.lift_clear_score: 0.596
- phase_breakdown.place_score: 0.874
- grasp_place_fitness: 0.639

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.639
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.327
- **Median Q (composite search score)**: 0.187
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: transport_1.transport_speed
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4329,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00644,"descend_2.place_z_offset":0.0054,"lift_1.lift_height":0.13719,"transport_1.approach_height":0.12536,"transport_1.arc_height":0.05011,"transport_1.transport_speed":0.01},"optimized_scores":{"best_composite_score":0.18533,"best_fitness_score":0.60533,"best_task_score":0.23852},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":27.0,"contact_point_centroid":[0.57484,0.23165,-0.01218],"force_p95":2.52032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.52595,"mean_force":1.87584,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57119,0.21267,0.3452]},{"body_a":"world","body_b":"grasp_target","contact_count":1086.0,"contact_point_centroid":[0.57594,0.24295,-0.00332],"force_p95":0.31847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73289,"mean_force":0.14429,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57467,0.21978,0.2949]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.47937,0.04371,-0.00142],"force_p95":0.50071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7258,"mean_force":0.09171,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47279,0.04533,0.02956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13718.0,"contact_point_centroid":[0.47148,0.06422,0.08558],"force_p95":0.09541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33828,"mean_force":0.05877,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47041,0.04511,0.0836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14407.0,"contact_point_centroid":[0.47153,0.02614,0.08803],"force_p95":0.08762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3022,"mean_force":0.05541,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47041,0.04511,0.0863]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48282,0.04809,-0.00238],"force_p95":0.20915,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2888,"mean_force":0.14992,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47482,0.04555,0.02778]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10285.0,"contact_point_centroid":[0.49976,0.07217,0.24634],"force_p95":0.13222,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26308,"mean_force":0.08135,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49597,0.09062,0.24741]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10120.0,"contact_point_centroid":[0.50217,0.11234,0.25095],"force_p95":0.12858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21791,"mean_force":0.08323,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49797,0.09388,0.2517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5694.0,"contact_point_centroid":[0.47456,0.02631,0.02928],"force_p95":0.08052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1623,"mean_force":0.04535,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47439,0.0455,0.02734]},{"body_a":"world","body_b":"grasp_target","contact_count":3332.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48847,0.02289,0.16458]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57613,0.24279,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57473,0.22414,0.24468]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6192.0,"contact_point_centroid":[0.47454,0.06493,0.02925],"force_p95":0.08152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08705,"mean_force":0.04514,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4744,0.0455,0.02735]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1130.0,"contact_point_centroid":[0.57514,0.21991,0.29596],"force_p95":0.01277,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01498,"mean_force":0.0107,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57472,0.21989,0.29371]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.5771,0.2251,0.24297],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01001,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5766,0.22506,0.24065]}],"total_contact_groups":14},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57613,0.24279,0.01602],"final_tcp_position":[0.57797,0.22557,0.24432],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273006.62174,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3332.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47916,0.04592,0.0323],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04582,0.02489],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29262,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19168,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13690.0,"raw_peak_contact_force":0.2888,"tcp_end":[0.47437,0.04549,0.02732],"tcp_start":[0.47437,0.04549,0.02732],"tcp_to_object_dist_end":0.0086,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.48653,0.04553,0.14225],"object_pos_start":[0.48261,0.0458,0.02494],"object_to_goal_dist_end":0.22469,"object_to_goal_dist_start":0.29259,"object_z_max":0.14214,"peak_contact_force":0.10614,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28274.0,"raw_peak_contact_force":0.7258,"subtask_id":"lift_clear","tcp_end":[0.47062,0.04514,0.15299],"tcp_start":[0.47437,0.04549,0.02732],"tcp_to_object_dist_end":0.0192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57829,0.23481,-0.01233],"object_pos_start":[0.48653,0.04553,0.14225],"object_to_goal_dist_end":0.24291,"object_to_goal_dist_start":0.22469,"object_z_max":0.31021,"peak_contact_force":1.79665,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20432.0,"raw_peak_contact_force":2.52595,"tcp_end":[0.57244,0.21472,0.34558],"tcp_start":[0.47062,0.04514,0.15299],"tcp_to_object_dist_end":0.35852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.57613,0.24279,0.01602],"object_pos_start":[0.57829,0.23481,-0.01233],"object_to_goal_dist_end":0.21499,"object_to_goal_dist_start":0.24291,"object_z_max":0.01773,"peak_contact_force":273006.62174,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2216.0,"raw_peak_contact_force":1.73289,"subtask_id":"place","tcp_end":[0.57797,0.22557,0.24432],"tcp_start":[0.57244,0.21472,0.34558],"tcp_to_object_dist_end":0.22896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57613,0.24279,0.01602],"object_pos_start":[0.57613,0.24279,0.01602],"object_to_goal_dist_end":0.21499,"object_to_goal_dist_start":0.21499,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57368,0.2236,0.26441],"tcp_start":[0.57797,0.22557,0.24432],"tcp_to_object_dist_end":0.24914,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44076,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00441,"descend_2.place_z_offset":0.00455,"lift_1.lift_height":0.11079,"transport_1.approach_height":0.12,"transport_1.arc_height":0.05698,"transport_1.transport_speed":0.01014},"optimized_scores":{"best_composite_score":0.18659,"best_fitness_score":0.60659,"best_task_score":0.26175},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1089.0,"contact_point_centroid":[0.6154,0.1664,-0.00335],"force_p95":0.59756,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43023,"mean_force":0.18273,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59793,0.20121,0.25372]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.53428,-0.01968,-0.0012],"force_p95":0.39663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57212,"mean_force":0.08312,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52365,-0.02008,0.03737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10696.0,"contact_point_centroid":[0.52247,-0.00098,0.0826],"force_p95":0.09871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30309,"mean_force":0.06058,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52107,-0.02002,0.08048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11518.0,"contact_point_centroid":[0.5225,-0.03897,0.081],"force_p95":0.09492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30213,"mean_force":0.05731,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52106,-0.02002,0.07943]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10275.0,"contact_point_centroid":[0.54434,0.05787,0.22481],"force_p95":0.15126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23635,"mean_force":0.08578,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53978,0.03934,0.2248]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53707,-0.02111,-0.00213],"force_p95":0.15375,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22266,"mean_force":0.13246,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5258,-0.02012,0.03614]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11425.0,"contact_point_centroid":[0.54574,0.0248,0.22743],"force_p95":0.12129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18411,"mean_force":0.07808,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54119,0.04314,0.2277]},{"body_a":"world","body_b":"grasp_target","contact_count":3312.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51411,-0.01006,0.16924]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61546,0.16639,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60116,0.21898,0.2151]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5807.0,"contact_point_centroid":[0.52528,-0.0009,0.03789],"force_p95":0.06996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1108,"mean_force":0.04513,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52533,-0.02011,0.0356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6271.0,"contact_point_centroid":[0.52514,-0.03934,0.03743],"force_p95":0.06887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07346,"mean_force":0.04312,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52534,-0.02011,0.0356]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1049.0,"contact_point_centroid":[0.599,0.20303,0.25215],"force_p95":0.01278,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01611,"mean_force":0.01078,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59856,0.20302,0.24993]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.60335,0.22004,0.21361],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01003,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60335,0.22002,0.21161]}],"total_contact_groups":13},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61546,0.16639,0.01602],"final_tcp_position":[0.60481,0.22029,0.21526],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.43023,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3312.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53043,-0.02018,0.04161],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02033,0.0256],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3162,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14803,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13882.0,"raw_peak_contact_force":0.22266,"tcp_end":[0.52531,-0.02011,0.03557],"tcp_start":[0.52531,-0.02011,0.03557],"tcp_to_object_dist_end":0.01533,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.53556,-0.02006,0.1179],"object_pos_start":[0.53695,-0.02031,0.02563],"object_to_goal_dist_end":0.27388,"object_to_goal_dist_start":0.31617,"object_z_max":0.11779,"peak_contact_force":0.10379,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22364.0,"raw_peak_contact_force":0.57212,"subtask_id":"lift_clear","tcp_end":[0.52117,-0.02001,0.13401],"tcp_start":[0.52531,-0.02011,0.03557],"tcp_to_object_dist_end":0.0216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60202,0.16513,0.22692],"object_pos_start":[0.53556,-0.02006,0.1179],"object_to_goal_dist_end":0.06612,"object_to_goal_dist_start":0.27388,"object_z_max":0.28426,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21700.0,"raw_peak_contact_force":0.23635,"tcp_end":[0.58973,0.17472,0.31522],"tcp_start":[0.52117,-0.02001,0.13401],"tcp_to_object_dist_end":0.08966,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.61546,0.16639,0.01602],"object_pos_start":[0.60202,0.16513,0.22692],"object_to_goal_dist_end":0.20105,"object_to_goal_dist_start":0.06612,"object_z_max":0.22692,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2138.0,"raw_peak_contact_force":2.43023,"subtask_id":"place","tcp_end":[0.60481,0.22029,0.21526],"tcp_start":[0.58973,0.17472,0.31522],"tcp_to_object_dist_end":0.20668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61546,0.16639,0.01602],"object_pos_start":[0.61546,0.16639,0.01602],"object_to_goal_dist_end":0.20105,"object_to_goal_dist_start":0.20105,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59991,0.21838,0.23452],"tcp_start":[0.60481,0.22029,0.21526],"tcp_to_object_dist_end":0.22514,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43256,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00491,"descend_2.place_z_offset":-0.00513,"lift_1.lift_height":0.10745,"transport_1.approach_height":0.1141,"transport_1.arc_height":0.07428,"transport_1.transport_speed":0.04939},"optimized_scores":{"best_composite_score":0.21877,"best_fitness_score":0.63877,"best_task_score":0.32711},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.63715,0.11851,-0.00996],"force_p95":1.75366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07463,"mean_force":0.93428,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.62012,0.14433,0.28861]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.63665,0.11794,-0.0027],"force_p95":0.13456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68666,"mean_force":0.12526,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62395,0.15398,0.23351]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.54269,-0.02689,-0.00125],"force_p95":0.3931,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57845,"mean_force":0.08428,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53166,-0.02751,0.03715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10739.0,"contact_point_centroid":[0.53077,-0.04634,0.07858],"force_p95":0.0976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31344,"mean_force":0.05875,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52908,-0.02742,0.0771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9911.0,"contact_point_centroid":[0.53074,-0.00841,0.08047],"force_p95":0.10176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30493,"mean_force":0.06227,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52909,-0.02742,0.0784]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54568,-0.02896,-0.00218],"force_p95":0.16485,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2339,"mean_force":0.13586,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53386,-0.02758,0.0359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9443.0,"contact_point_centroid":[0.54935,0.02526,0.21731],"force_p95":0.15114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22366,"mean_force":0.08625,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54472,0.00674,0.21726]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10471.0,"contact_point_centroid":[0.55134,-0.00792,0.22084],"force_p95":0.12147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20555,"mean_force":0.07872,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54676,0.01044,0.22106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6083.0,"contact_point_centroid":[0.53308,-0.00831,0.03816],"force_p95":0.06936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15263,"mean_force":0.04316,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53338,-0.02756,0.03533]},{"body_a":"world","body_b":"grasp_target","contact_count":3384.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5182,-0.01383,0.16901]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63666,0.1181,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62333,0.16016,0.17901]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6622.0,"contact_point_centroid":[0.53294,-0.04686,0.03761],"force_p95":0.0695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07522,"mean_force":0.04127,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53339,-0.02756,0.03534]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1159.0,"contact_point_centroid":[0.62454,0.15433,0.23265],"force_p95":0.01245,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01065,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62408,0.15432,0.23047]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.62643,0.161,0.17774],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.01028,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62592,0.16098,0.17549]}],"total_contact_groups":14},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63666,0.1181,0.01602],"final_tcp_position":[0.62771,0.16136,0.17949],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":249.16751,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3384.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53854,-0.02769,0.04152],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.02789,0.02546],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26027,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15713,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14509.0,"raw_peak_contact_force":0.2339,"tcp_end":[0.53336,-0.02756,0.0353],"tcp_start":[0.53336,-0.02756,0.03531],"tcp_to_object_dist_end":0.01566,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54364,-0.02753,0.11386],"object_pos_start":[0.54555,-0.02787,0.0255],"object_to_goal_dist_end":0.2213,"object_to_goal_dist_start":0.26023,"object_z_max":0.11375,"peak_contact_force":249.16751,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20802.0,"raw_peak_contact_force":0.57845,"subtask_id":"lift_clear","tcp_end":[0.52916,-0.02741,0.13015],"tcp_start":[0.53336,-0.02756,0.0353],"tcp_to_object_dist_end":0.02179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63707,0.12387,-0.00824],"object_pos_start":[0.54364,-0.02753,0.11386],"object_to_goal_dist_end":0.18971,"object_to_goal_dist_start":0.2213,"object_z_max":0.26657,"peak_contact_force":0.73225,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19985.0,"raw_peak_contact_force":2.07463,"tcp_end":[0.62178,0.14737,0.28775],"tcp_start":[0.52916,-0.02741,0.13015],"tcp_to_object_dist_end":0.29732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.63666,0.1181,0.01602],"object_pos_start":[0.63707,0.12387,-0.00824],"object_to_goal_dist_end":0.16762,"object_to_goal_dist_start":0.18971,"object_z_max":0.0171,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2307.0,"raw_peak_contact_force":0.68666,"subtask_id":"place","tcp_end":[0.62771,0.16136,0.17949],"tcp_start":[0.62178,0.14737,0.28775],"tcp_to_object_dist_end":0.16933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63666,0.1181,0.01602],"object_pos_start":[0.63666,0.1181,0.01602],"object_to_goal_dist_end":0.16762,"object_to_goal_dist_start":0.16762,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62179,0.15966,0.19839],"tcp_start":[0.62771,0.16136,0.17949],"tcp_to_object_dist_end":0.18764,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```