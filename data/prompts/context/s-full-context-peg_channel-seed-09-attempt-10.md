## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0973 | 0.06 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.3200 | 0.56 | ✅ accepted |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0222 | 0.32 | ❌ rejected |
| 7 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.1539 | 0.12 | ❌ rejected |
| 6 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2651 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
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

## Current Skill (Q=-0.097) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.16
  weight: 0.2
- id: align_to_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.3
- id: push_through
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_prep
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
    - 0.16
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: descend_to_peg_height
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_to_peg
- id: lateral_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    contact_x_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
  guards:
  - id: force_high
    when: during_phase
    predicate: force_below
    threshold: 60.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: align_to_peg
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.22
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.18
      - 0.26
      default: 0.22
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_lateral_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_through

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_prep** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.16], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg_height** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **lateral_contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
    - contact_x_offset: status=consumed; consumers=target.offset.x (replace)
  - guards:
    - id=force_high, when=during_phase, predicate=force_below, on_failure=continue, threshold=60.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.22, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.097
- **task_score** (E): 0.062
- **fitness_score**: 0.246  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prep | 1.00 | 1.00 | 0.1254 |
| descend_to_peg_height | 1.00 | 1.00 | 0.1537 |
| lateral_contact | 0.67 | 1.00 | 0.0359 |
| push_channel | 0.00 | 1.00 | 0.0014 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prep | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.129, 0.200) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.545 | 4.034 |
| descend_to_peg_height | descend | 1.00 / step_budget | (0.508, 0.129, 0.200)→(0.499, 0.117, 0.048) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.571 | 0.588 |
| lateral_contact | contact | 0.67 / force_exceeded | (0.499, 0.117, 0.048)→(0.497, 0.085, 0.034) | (0.502, 0.067, 0.034)→(0.504, 0.056, 0.036) | 0.147→0.136 | 1.00 / 1.667 | 2612.755 | 3.822 |
| push_channel | push | 0.00 / guard_failure | (0.510, 0.069, 0.027)→(0.511, 0.068, 0.026) | (0.504, 0.056, 0.036)→(0.505, 0.039, 0.036) | 0.136→0.119 | 1.00 / 3.000 | 1080.866 | 2059.260 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.163
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.070
- phase_score: 0.361
- phase_breakdown.push_through_score: 0.095
- phase_breakdown.align_to_peg_score: 0.555
- phase_breakdown.reach_peg_score: 0.736

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.253
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.070
- **Median Q (composite search score)**: -0.019
- **K-run variance**: 0.0128
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.226


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54955,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.14262,"approach_prep.approach_speed":0.14562,"descend_to_peg_height.descend_speed":0.07027,"lateral_contact.contact_force_threshold":7.74424,"lateral_contact.contact_speed":0.02378,"lateral_contact.contact_x_offset":-0.00151,"push_channel.push_distance":0.15887,"push_channel.push_lateral_offset":-0.00243,"push_channel.push_speed":0.03264},"optimized_scores":{"best_composite_score":-0.01554,"best_fitness_score":0.24446,"best_task_score":0.06975},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.5259,0.0745,0.05985],"force_p95":1397.5362,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1413.90469,"mean_force":1245.13143,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50995,0.07265,0.03043]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50494,0.0692,0.03884],"force_p95":31.44508,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.49917,"mean_force":15.26947,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50284,0.08104,0.03397]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50371,0.04882,0.00987],"force_p95":27.19411,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.30703,"mean_force":15.32877,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50642,0.07698,0.0322]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52519,0.04828,0.03038],"force_p95":21.23649,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.56513,"mean_force":6.20012,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50509,0.0784,0.03285]},{"body_a":"peg","body_b":"channel_base_body","contact_count":221.0,"contact_point_centroid":[0.50549,0.06296,0.00932],"force_p95":0.68749,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.60781,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51181,0.15984,0.24224]},{"body_a":"peg","body_b":"channel_base_body","contact_count":673.0,"contact_point_centroid":[0.50594,0.05531,0.00958],"force_p95":2.8424,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.22374,"mean_force":1.1889,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50077,0.09671,0.03914]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.5008,0.19633,0.29461]},{"body_a":"attachment","body_b":"peg","contact_count":245.0,"contact_point_centroid":[0.50358,0.0763,0.04286],"force_p95":2.64369,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.96389,"mean_force":1.9932,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50056,0.08813,0.03646]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52501,0.05548,0.02249],"force_p95":1.00528,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04018,"mean_force":0.7259,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50055,0.08434,0.03538]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.50595,0.06293,0.00938],"force_p95":0.55214,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55641,"mean_force":0.54654,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51302,0.11965,0.12235]}],"total_contact_groups":10},"final_pose_error":0.14556,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50764,0.03686,0.03536],"final_tcp_position":[0.5118,0.06954,0.02957],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3918.71301,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":249.0,"n_steps_budget":660.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55664,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":255.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52275,0.12593,0.19566],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06298,0.03381],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54915,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":351.0,"raw_peak_contact_force":0.55641,"subtask_id":"align_to_peg","tcp_end":[0.50446,0.1137,0.04838],"tcp_start":[0.52275,0.12593,0.19566],"tcp_to_object_dist_end":0.0528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":685.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.05432,0.03561],"object_pos_start":[0.50593,0.06298,0.03381],"object_to_goal_dist_end":0.13457,"object_to_goal_dist_start":0.14324,"object_z_max":0.03562,"peak_contact_force":3918.71301,"phase_name":"lateral_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":945.0,"raw_peak_contact_force":3.22374,"subtask_id":"align_to_peg","tcp_end":[0.50055,0.0836,0.03516],"tcp_start":[0.50446,0.1137,0.04838],"tcp_to_object_dist_end":0.02999,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50736,0.04152,0.03524],"object_pos_start":[0.50699,0.05432,0.03561],"object_to_goal_dist_end":0.12184,"object_to_goal_dist_start":0.13457,"object_z_max":0.03569,"peak_contact_force":1.20145,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":25.0,"raw_peak_contact_force":1413.90469,"subtask_id":"push_through","tcp_end":[0.5118,0.06954,0.02957],"tcp_start":[0.51106,0.07098,0.02987],"tcp_to_object_dist_end":0.02893,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12879,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.15705,"approach_prep.approach_speed":0.12675,"descend_to_peg_height.descend_speed":0.05998,"lateral_contact.contact_force_threshold":5.97231,"lateral_contact.contact_speed":0.0234,"lateral_contact.contact_x_offset":-0.00973,"push_channel.push_distance":0.18321,"push_channel.push_lateral_offset":-0.00079,"push_channel.push_speed":0.02358},"optimized_scores":{"best_composite_score":-0.0188,"best_fitness_score":0.2412,"best_task_score":0.06238},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54025,0.07775,0.05918],"force_p95":3262.21829,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3264.59918,"mean_force":2881.94542,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50882,0.05681,0.02479]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.5259,0.06063,0.05985],"force_p95":3115.92477,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3127.75744,"mean_force":2564.12391,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50882,0.05681,0.02479]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50259,0.05922,0.03825],"force_p95":31.34065,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.4543,"mean_force":16.11111,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49892,0.0704,0.03259]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50765,0.02908,0.00979],"force_p95":29.13667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.58583,"mean_force":9.55812,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50359,0.06412,0.02914]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52528,0.03595,0.03018],"force_p95":24.39836,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.51846,"mean_force":6.4149,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5022,0.06597,0.03015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":220.0,"contact_point_centroid":[0.50545,0.05669,0.00932],"force_p95":0.69924,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.61886,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51493,0.15693,0.24869]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.50119,0.19566,0.29458]},{"body_a":"attachment","body_b":"peg","contact_count":298.0,"contact_point_centroid":[0.50136,0.06845,0.04372],"force_p95":2.80017,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.74091,"mean_force":1.95089,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.4966,0.07993,0.03597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":737.0,"contact_point_centroid":[0.50587,0.04761,0.00961],"force_p95":2.93778,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.49318,"mean_force":1.2481,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.49829,0.08857,0.03863]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52501,0.0498,0.01131],"force_p95":1.16473,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35957,"mean_force":0.7955,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.49598,0.07632,0.03494]},{"body_a":"peg","body_b":"channel_base_body","contact_count":389.0,"contact_point_centroid":[0.50615,0.05651,0.00937],"force_p95":0.61968,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62364,"mean_force":0.54661,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51625,0.11401,0.12852]}],"total_contact_groups":11},"final_pose_error":0.16465,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50507,0.01924,0.03632],"final_tcp_position":[0.51019,0.05469,0.0237],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":3919.5279,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":249.0,"n_steps_budget":720.0,"object_pos_end":[0.50613,0.05663,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.5274,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":257.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.52851,0.12087,0.20803],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05667,0.03377],"object_pos_start":[0.50613,0.05663,0.03377],"object_to_goal_dist_end":0.13695,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":0.61849,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":389.0,"raw_peak_contact_force":0.62364,"subtask_id":"align_to_peg","tcp_end":[0.50514,0.10747,0.0484],"tcp_start":[0.52851,0.12087,0.20803],"tcp_to_object_dist_end":0.05287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.50678,0.04628,0.03613],"object_pos_start":[0.50612,0.05667,0.03377],"object_to_goal_dist_end":0.12652,"object_to_goal_dist_start":0.13695,"object_z_max":0.03611,"peak_contact_force":3919.5279,"phase_name":"lateral_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1049.0,"raw_peak_contact_force":3.74091,"subtask_id":"align_to_peg","tcp_end":[0.49563,0.07431,0.03437],"tcp_start":[0.50514,0.10747,0.0484],"tcp_to_object_dist_end":0.03022,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50576,0.02348,0.03594],"object_pos_start":[0.50678,0.04628,0.03613],"object_to_goal_dist_end":0.10372,"object_to_goal_dist_start":0.12652,"object_z_max":0.03627,"peak_contact_force":3240.79026,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":35.0,"raw_peak_contact_force":3264.59918,"subtask_id":"push_through","tcp_end":[0.51019,0.05469,0.0237],"tcp_start":[0.50962,0.05563,0.02406],"tcp_to_object_dist_end":0.03381,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.1413,"approach_prep.approach_speed":0.09685,"descend_to_peg_height.descend_speed":0.02877,"lateral_contact.contact_force_threshold":4.66456,"lateral_contact.contact_speed":0.02024,"lateral_contact.contact_x_offset":0.01177,"push_channel.push_distance":0.15374,"push_channel.push_lateral_offset":0.0056,"push_channel.push_speed":0.02555},"optimized_scores":{"best_composite_score":-0.25743,"best_fitness_score":0.25257,"best_task_score":0.05477},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52562,0.08573,0.0599],"force_p95":1480.54085,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1499.27697,"mean_force":1292.92933,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50898,0.0829,0.027]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49783,0.05652,0.00988],"force_p95":29.56587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.60559,"mean_force":9.4339,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50218,0.09013,0.03078]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50076,0.08154,0.04632],"force_p95":31.40855,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.88315,"mean_force":13.00886,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49957,0.09282,0.03211]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.49528,0.06942,0.00963],"force_p95":2.53361,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.50159,"mean_force":1.23787,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.49058,0.11194,0.0383]},{"body_a":"attachment","body_b":"peg","contact_count":438.0,"contact_point_centroid":[0.49511,0.09119,0.04226],"force_p95":2.60773,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.18739,"mean_force":1.74524,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.49349,0.10318,0.0357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":205.0,"contact_point_centroid":[0.49468,0.07987,0.00934],"force_p95":0.67452,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.6088,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.48529,0.1682,0.24313]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.49836,0.19683,0.2944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":407.0,"contact_point_centroid":[0.49376,0.08,0.00938],"force_p95":0.57183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58307,"mean_force":0.54654,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.47961,0.13568,0.12301]}],"total_contact_groups":8},"final_pose_error":0.13823,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50134,0.0477,0.03708],"final_tcp_position":[0.51055,0.08047,0.02575],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":1499.27697,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":233.0,"n_steps_budget":930.0,"object_pos_end":[0.49382,0.07997,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54992,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":240.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.47342,0.14127,0.19697],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.4938,0.07995,0.03378],"object_pos_start":[0.49382,0.07997,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16021,"object_z_max":0.03379,"peak_contact_force":0.54438,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":407.0,"raw_peak_contact_force":0.58307,"subtask_id":"align_to_peg","tcp_end":[0.48814,0.13038,0.04766],"tcp_start":[0.47342,0.14127,0.19697],"tcp_to_object_dist_end":0.05261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49833,0.06659,0.0351],"object_pos_start":[0.4938,0.07995,0.03378],"object_to_goal_dist_end":0.14668,"object_to_goal_dist_start":0.16019,"object_z_max":0.03521,"peak_contact_force":0.02546,"phase_name":"lateral_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1415.0,"raw_peak_contact_force":4.50159,"subtask_id":"align_to_peg","tcp_end":[0.49578,0.09652,0.03383],"tcp_start":[0.48814,0.13038,0.04766],"tcp_to_object_dist_end":0.03006,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50085,0.05172,0.03608],"object_pos_start":[0.49833,0.06659,0.0351],"object_to_goal_dist_end":0.13178,"object_to_goal_dist_start":0.14668,"object_z_max":0.0366,"peak_contact_force":0.60644,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":21.0,"raw_peak_contact_force":1499.27697,"subtask_id":"push_through","tcp_end":[0.51055,0.08047,0.02575],"tcp_start":[0.50995,0.08159,0.02623],"tcp_to_object_dist_end":0.03206,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```