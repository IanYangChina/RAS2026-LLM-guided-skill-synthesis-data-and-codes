## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.4170 | 0.52 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0835 | 0.01 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.4290 | 0.69 | ✅ accepted |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0845 | 0.01 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0630 | 0.54 | ❌ rejected |

**Proposal policy**: task_score is 0.52 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=0.417) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
  weight: 0.3
- id: push_complete
  metric: goal_progress
  weight: 0.4
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - -0.003
    - 0.0
    - 0.0
  subtask_id: reach_contact
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push_complete
- id: retract_away
  type: retract
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[-0.003, 0.0, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed
- **retract_away** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.417
- **task_score** (E): 0.519
- **fitness_score**: 0.610  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_peg | 1.00 | 0.2541 |
| contact_peg | 1.00 | 0.0557 |
| push_channel | 0.33 | 0.0527 |
| retract_away | 0.67 | 0.1114 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.178, 0.049) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 |
| contact_peg | contact | 1.00 / force_exceeded | (0.505, 0.178, 0.049)→(0.503, 0.125, 0.034) | (0.502, 0.098, 0.034)→(0.507, 0.084, 0.035) | 0.178→0.164 |
| push_channel | push | 0.33 / guard_failure | (0.504, 0.066, 0.034)→(0.507, 0.014, 0.034) | (0.507, 0.084, 0.035)→(0.506, -0.028, 0.035) | 0.164→0.056 |
| retract_away | retract | 0.67 / step_budget | (0.507, 0.014, 0.034)→(0.499, -0.047, 0.116) | (0.506, -0.029, 0.035)→(0.504, -0.043, 0.031) | 0.056→0.040 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- terminal_score: 1.000
- phase_score: 0.847
- phase_breakdown.push_complete_score: 0.954
- phase_breakdown.reach_approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.908
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.331
- **K-run variance**: 0.0800
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.455


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04167,"average_solve_count":288.0,"average_success_count":288.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.0487,"contact_peg.contact_force_threshold":8.78287,"contact_peg.contact_speed":0.04306,"push_channel.push_distance":0.17441,"push_channel.push_speed":0.03197,"retract_away.retract_speed":0.09143},"optimized_scores":{"best_composite_score":0.79825,"best_fitness_score":0.90825,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":441.0,"contact_point_centroid":[0.50174,-0.06822,0.06278],"force_p95":48.48292,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.44781,"mean_force":33.26473,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49748,-0.05765,0.05951]},{"body_a":"peg","body_b":"channel_base_body","contact_count":473.0,"contact_point_centroid":[0.50785,-0.10061,0.06411],"force_p95":48.5334,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.42356,"mean_force":31.16381,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49747,-0.05837,0.06183]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50571,-0.10037,0.05045],"force_p95":49.76198,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.10254,"mean_force":27.73567,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50224,-0.05348,0.03003]},{"body_a":"attachment","body_b":"peg","contact_count":375.0,"contact_point_centroid":[0.50387,0.02308,0.04404],"force_p95":22.20246,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.86967,"mean_force":5.54543,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49956,0.03468,0.02861]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":264.0,"contact_point_centroid":[0.52516,0.02249,0.03503],"force_p95":21.95395,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.60024,"mean_force":5.14081,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49913,0.05147,0.02843]},{"body_a":"peg","body_b":"channel_base_body","contact_count":158.0,"contact_point_centroid":[0.5064,-0.01141,0.0099],"force_p95":17.91225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.24643,"mean_force":5.41299,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49972,0.03361,0.02878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":194.0,"contact_point_centroid":[0.50108,-0.07676,0.00905],"force_p95":1.97855,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.7334,"mean_force":0.82067,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.4972,-0.07412,0.11264]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":104.0,"contact_point_centroid":[0.52505,-0.08268,0.05578],"force_p95":8.81796,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.65753,"mean_force":4.35175,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49723,-0.05988,0.07129]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":27.0,"contact_point_centroid":[0.47498,-0.07858,0.04077],"force_p95":6.64253,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.0166,"mean_force":3.67049,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49668,-0.05861,0.07172]},{"body_a":"peg","body_b":"channel_base_body","contact_count":914.0,"contact_point_centroid":[0.50383,0.1042,0.00956],"force_p95":4.29566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.88297,"mean_force":1.38099,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50123,0.15559,0.03759]},{"body_a":"attachment","body_b":"peg","contact_count":282.0,"contact_point_centroid":[0.50325,0.11985,0.04247],"force_p95":4.3807,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.5912,"mean_force":2.87793,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50044,0.13177,0.03296]},{"body_a":"peg","body_b":"channel_base_body","contact_count":814.0,"contact_point_centroid":[0.50354,0.11169,0.00938],"force_p95":0.61233,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55399,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50207,0.19487,0.17092]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49977,0.19958,0.29907]}],"total_contact_groups":13},"final_pose_error":0.01121,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50194,-0.07572,0.03407],"final_tcp_position":[0.49691,-0.07816,0.12938],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"phases":[{"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.1118,0.03379],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.50583,0.19087,0.04898],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08054,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,0.09222,0.03541],"object_pos_start":[0.50374,0.1118,0.03379],"object_to_goal_dist_end":0.17241,"object_to_goal_dist_start":0.19194,"object_z_max":0.03555,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.50016,0.12161,0.03105],"tcp_start":[0.50583,0.19087,0.04898],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,-0.08292,0.03557],"object_pos_start":[0.50687,0.09222,0.03541],"object_to_goal_dist_end":0.00814,"object_to_goal_dist_start":0.17241,"object_z_max":0.03681,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.50219,-0.05418,0.02995],"tcp_start":[0.50223,-0.05404,0.03],"tcp_to_object_dist_end":0.02955,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.50194,-0.07572,0.03407],"object_pos_start":[0.50633,-0.08342,0.03555],"object_to_goal_dist_end":0.00756,"object_to_goal_dist_start":0.00845,"object_z_max":0.06727,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49691,-0.07816,0.12938],"tcp_start":[0.50219,-0.05418,0.02995],"tcp_to_object_dist_end":0.09547,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88013,"average_solve_count":317.0,"average_success_count":317.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.01896,"contact_peg.contact_force_threshold":8.54713,"contact_peg.contact_speed":0.04698,"push_channel.push_distance":0.14961,"push_channel.push_speed":0.01707,"retract_away.retract_speed":0.05857},"optimized_scores":{"best_composite_score":0.33148,"best_fitness_score":0.69148,"best_task_score":0.46141},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":308.0,"contact_point_centroid":[0.52524,0.03043,0.03261],"force_p95":21.75572,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.6606,"mean_force":3.98769,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49407,0.0575,0.02827]},{"body_a":"attachment","body_b":"peg","contact_count":338.0,"contact_point_centroid":[0.50121,0.03407,0.0431],"force_p95":21.98218,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.61268,"mean_force":4.99902,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49519,0.0451,0.02869]},{"body_a":"peg","body_b":"channel_base_body","contact_count":157.0,"contact_point_centroid":[0.50626,0.00224,0.00988],"force_p95":17.68048,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.48101,"mean_force":5.50402,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4953,0.04482,0.02878]},{"body_a":"attachment","body_b":"peg","contact_count":307.0,"contact_point_centroid":[0.49589,0.12363,0.04794],"force_p95":5.59369,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.00978,"mean_force":3.2821,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48954,0.13489,0.03255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":934.0,"contact_point_centroid":[0.49878,0.10974,0.0096],"force_p95":4.71054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.28285,"mean_force":1.47962,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48575,0.15962,0.03759]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":46.0,"contact_point_centroid":[0.52508,0.09665,0.0495],"force_p95":4.98094,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.08139,"mean_force":3.29783,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49127,0.12362,0.03026]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":216.0,"contact_point_centroid":[0.52509,-0.07202,0.0388],"force_p95":2.89482,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.12489,"mean_force":0.81703,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49857,-0.04343,0.04694]},{"body_a":"attachment","body_b":"peg","contact_count":219.0,"contact_point_centroid":[0.50188,-0.05656,0.05239],"force_p95":2.99671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.9224,"mean_force":0.84133,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49807,-0.04514,0.05098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":801.0,"contact_point_centroid":[0.49621,0.11908,0.00943],"force_p95":0.61471,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55031,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49071,0.19828,0.17055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.50613,-0.0746,0.00962],"force_p95":0.66941,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79227,"mean_force":0.5252,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49766,-0.05664,0.07918]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49955,0.19955,0.29798]}],"total_contact_groups":11},"final_pose_error":0.01405,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50663,-0.06776,0.03386],"final_tcp_position":[0.49689,-0.0761,0.12687],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"phases":[{"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11902,0.0339],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.48344,0.19765,0.04951],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08114,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":985.0,"n_steps_budget":1000.0,"object_pos_end":[0.50748,0.09592,0.03643],"object_pos_start":[0.49602,0.11902,0.0339],"object_to_goal_dist_end":0.17612,"object_to_goal_dist_start":0.19915,"object_z_max":0.03641,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.49149,0.12199,0.02991],"tcp_start":[0.48344,0.19765,0.04951],"tcp_to_object_dist_end":0.03127,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.50669,-0.06531,0.03597],"object_pos_start":[0.50748,0.09592,0.03643],"object_to_goal_dist_end":0.01663,"object_to_goal_dist_start":0.17612,"object_z_max":0.03683,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.50211,-0.03544,0.03099],"tcp_start":[0.49149,0.12199,0.02991],"tcp_to_object_dist_end":0.03064,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50663,-0.06776,0.03386],"object_pos_start":[0.50669,-0.06531,0.03597],"object_to_goal_dist_end":0.01522,"object_to_goal_dist_start":0.01663,"object_z_max":0.03851,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49689,-0.0761,0.12687],"tcp_start":[0.50211,-0.03544,0.03099],"tcp_to_object_dist_end":0.09389,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92121,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.05591,"contact_peg.contact_force_threshold":4.90077,"contact_peg.contact_speed":0.03906,"push_channel.push_distance":0.1242,"push_channel.push_speed":0.02559,"retract_away.retract_speed":0.05051},"optimized_scores":{"best_composite_score":0.1213,"best_fitness_score":0.2313,"best_task_score":0.09564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":177.0,"contact_point_centroid":[0.52501,0.11848,0.06],"force_p95":75.32735,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.38949,"mean_force":55.56524,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.5124,0.1239,0.04275]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.11997,0.06],"force_p95":57.40331,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.09141,"mean_force":45.8437,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51759,0.13114,0.04068]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":12.19596,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12.19596,"mean_force":12.19596,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51763,0.13121,0.04072]},{"body_a":"peg","body_b":"channel_base_body","contact_count":992.0,"contact_point_centroid":[0.50356,0.04552,0.00933],"force_p95":1.6231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.07662,"mean_force":0.71235,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50905,0.07709,0.06188]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47496,-0.0036,0.02452],"force_p95":8.12826,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.2253,"mean_force":4.68761,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50629,0.03916,0.07896]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.0361,0.02417],"force_p95":5.24456,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.29947,"mean_force":2.77196,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50451,0.01674,0.08964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.50579,0.06298,0.00937],"force_p95":0.55598,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56257,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51152,0.17131,0.16915]},{"body_a":"attachment","body_b":"peg","contact_count":186.0,"contact_point_centroid":[0.5076,0.06581,0.06089],"force_p95":2.29742,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.26195,"mean_force":0.61737,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50938,0.07766,0.06064]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49981,0.19897,0.29651]},{"body_a":"peg","body_b":"channel_base_body","contact_count":152.0,"contact_point_centroid":[0.50609,0.06317,0.00938],"force_p95":0.5519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55419,"mean_force":0.54663,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5199,0.13724,0.04296]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52029,0.05721,0.00939],"force_p95":0.54639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54644,"mean_force":0.54489,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51759,0.13114,0.04068]}],"total_contact_groups":11},"final_pose_error":0.10672,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50207,0.01568,0.02431],"final_tcp_position":[0.50434,0.01455,0.09068],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"phases":[{"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06304,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.5243,0.14483,0.04802],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08501,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.063,0.03381],"object_pos_start":[0.50599,0.06304,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.1433,"object_z_max":0.03381,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.51761,0.13115,0.04071],"tcp_start":[0.5243,0.14483,0.04802],"tcp_to_object_dist_end":0.06947,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06297,0.03381],"object_pos_start":[0.50603,0.063,0.03381],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.51754,0.13114,0.04061],"tcp_start":[0.51757,0.13113,0.04065],"tcp_to_object_dist_end":0.06947,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50207,0.01568,0.02431],"object_pos_start":[0.50598,0.06294,0.03381],"object_to_goal_dist_end":0.09698,"object_to_goal_dist_start":0.1432,"object_z_max":0.04078,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50434,0.01455,0.09068],"tcp_start":[0.51754,0.13114,0.04061],"tcp_to_object_dist_end":0.06642,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```