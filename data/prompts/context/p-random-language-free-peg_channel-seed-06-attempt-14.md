## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | 9 | 0.3126 | 0.77 | ✅ accepted |
| 13 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 10 | 0.2007 | 0.51 | ✅ accepted |
| 12 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | pose_tolerance | pose_tolerance | 8 | -0.2201 | 0.04 | ❌ rejected |
| 11 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | pose_tolerance | time_limit | 8 | 0.0712 | 0.42 | ✅ accepted |
| 10 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | pose_tolerance | time_limit | 8 | 0.0693 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.773, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=0.313) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.2
- id: contact_peg
  anchor: object
  offset:
  - 0.0
  - -0.03
  - 0.0
  weight: 0.2
- id: push_through
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    target_x_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    target_y_offset:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: approach_peg
- id: engage_peg
  type: contact
  generator: linear_cartesian
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
      distance: 0.03
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    contact_distance:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: contact_peg
- id: push_channel
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 8.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 39.5
    on_failure: continue
  subtask_id: push_through

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - target_x_offset: status=consumed; consumers=target.offset.x (replace)
    - target_y_offset: status=consumed; consumers=target.offset.y (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed
- **engage_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.03, mode=replace_offset_projection, sign=positive}, tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - contact_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=reduce_speed
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=39.5

## Design Metrics

- **Composite score**: 0.313
- **task_score** (E): 0.773
- **fitness_score**: 0.793  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2626 |
| engage_peg | 1.00 | 1.00 | 0.0552 |
| push_channel | 0.67 | 1.00 | 0.1065 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.500, 0.130, 0.049) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.333 | 0.781 | 7.632 |
| engage_peg | contact | 1.00 / step_budget | (0.500, 0.130, 0.049)→(0.496, 0.077, 0.033) | (0.501, 0.100, 0.034)→(0.498, 0.049, 0.036) | 0.180→0.130 | 1.00 / 2.333 | 3.192 | 13.965 |
| push_channel | push | 0.67 / time_limit | (0.496, 0.077, 0.033)→(0.494, -0.029, 0.030) | (0.498, 0.049, 0.036)→(0.504, -0.057, 0.036) | 0.130→0.028 | 1.00 / 3.000 | 19.595 | 25.158 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.773
- terminal_score: 1.000
- phase_score: 0.868
- phase_breakdown.approach_peg_score: 0.841
- phase_breakdown.push_through_score: 0.908
- phase_breakdown.contact_peg_score: 0.773

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.921
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.425
- **K-run variance**: 0.0289
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: push_channel.push_speed
- **Final σ (mean)**: 0.299


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48052,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06975,"approach_behind.target_x_offset":0.00644,"approach_behind.target_y_offset":0.02278,"engage_peg.contact_distance":0.02616,"engage_peg.contact_speed":0.02959,"push_channel.lateral_offset_x":0.00235,"push_channel.push_distance":0.14048,"push_channel.push_duration":9.26942,"push_channel.push_speed":0.07176},"optimized_scores":{"best_composite_score":0.42487,"best_fitness_score":0.90487,"best_task_score":0.93715},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":701.0,"contact_point_centroid":[0.49428,-0.01967,0.03057],"force_p95":16.69651,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.51797,"mean_force":2.50781,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49409,-0.00773,0.02845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.49785,-0.1008,0.05489],"force_p95":36.11385,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.89961,"mean_force":24.12297,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49348,-0.05406,0.02879]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50445,0.08469,0.05204],"force_p95":18.05994,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.58584,"mean_force":12.22017,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50531,0.09661,0.05186]},{"body_a":"peg","body_b":"channel_base_body","contact_count":883.0,"contact_point_centroid":[0.503,0.06702,0.00936],"force_p95":0.55416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.5377,"mean_force":0.60846,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50189,0.14618,0.17003]},{"body_a":"peg","body_b":"channel_base_body","contact_count":936.0,"contact_point_centroid":[0.49817,0.02584,0.00991],"force_p95":5.88838,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.59208,"mean_force":2.62277,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.50004,0.06739,0.03739]},{"body_a":"attachment","body_b":"peg","contact_count":877.0,"contact_point_centroid":[0.49983,0.05657,0.03766],"force_p95":5.73662,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.29071,"mean_force":2.41619,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.50009,0.0685,0.03759]},{"body_a":"peg","body_b":"channel_base_body","contact_count":754.0,"contact_point_centroid":[0.49368,-0.04356,0.00992],"force_p95":3.66536,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.9295,"mean_force":1.1926,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49417,-0.0059,0.0285]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":198.0,"contact_point_centroid":[0.47493,-0.02388,0.03319],"force_p95":0.95236,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.55516,"mean_force":0.36776,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4944,0.00602,0.02848]}],"total_contact_groups":8},"final_pose_error":0.07171,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49778,-0.08453,0.03488],"final_tcp_position":[0.4933,-0.05544,0.02856],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":45.51797,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.50185,0.06564,0.03567],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14572,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.43271,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":887.0,"raw_peak_contact_force":18.58584,"subtask_id":"approach_peg","tcp_end":[0.50544,0.09489,0.04762],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49454,0.01368,0.0346],"object_pos_start":[0.50185,0.06564,0.03567],"object_to_goal_dist_end":0.09399,"object_to_goal_dist_start":0.14572,"object_z_max":0.0379,"peak_contact_force":0.78802,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1813.0,"raw_peak_contact_force":9.59208,"subtask_id":"contact_peg","tcp_end":[0.49821,0.04343,0.03198],"tcp_start":[0.50544,0.09489,0.04762],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":872.0,"n_steps_budget":1000.0,"object_pos_end":[0.49778,-0.08453,0.03488],"object_pos_start":[0.49454,0.01368,0.0346],"object_to_goal_dist_end":0.00719,"object_to_goal_dist_start":0.09399,"object_z_max":0.03526,"peak_contact_force":45.51797,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1703.0,"raw_peak_contact_force":45.51797,"subtask_id":"push_through","tcp_end":[0.4933,-0.05544,0.02856],"tcp_start":[0.49821,0.04343,0.03198],"tcp_to_object_dist_end":0.03011,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18462,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.03798,"approach_behind.target_x_offset":0.00293,"approach_behind.target_y_offset":0.0273,"engage_peg.contact_distance":0.04009,"engage_peg.contact_speed":0.03059,"push_channel.lateral_offset_x":-0.00099,"push_channel.push_distance":0.17421,"push_channel.push_duration":11.10719,"push_channel.push_speed":0.08},"optimized_scores":{"best_composite_score":0.44058,"best_fitness_score":0.92058,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":935.0,"contact_point_centroid":[0.49399,0.07384,0.00993],"force_p95":3.28502,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.3594,"mean_force":1.22888,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.50286,0.11142,0.0378]},{"body_a":"attachment","body_b":"peg","contact_count":727.0,"contact_point_centroid":[0.49939,0.09986,0.03848],"force_p95":3.52154,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.03446,"mean_force":1.2372,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.50283,0.11129,0.03775]},{"body_a":"attachment","body_b":"peg","contact_count":754.0,"contact_point_centroid":[0.49513,0.01166,0.03176],"force_p95":5.39682,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.52305,"mean_force":1.20514,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49449,0.02349,0.02894]},{"body_a":"peg","body_b":"channel_base_body","contact_count":817.0,"contact_point_centroid":[0.49468,-0.01474,0.00992],"force_p95":5.13794,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.96126,"mean_force":1.38467,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49455,0.0238,0.02899]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52514,-0.06659,0.03077],"force_p95":5.07221,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.5341,"mean_force":2.67335,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49157,-0.04076,0.02952]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":164.0,"contact_point_centroid":[0.47495,0.0187,0.03274],"force_p95":1.18631,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.64671,"mean_force":0.43002,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49613,0.04843,0.02932]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":611.0,"contact_point_centroid":[0.47491,0.08018,0.03431],"force_p95":1.28488,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.69266,"mean_force":0.43693,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.5025,0.10851,0.03701]},{"body_a":"peg","body_b":"channel_base_body","contact_count":848.0,"contact_point_centroid":[0.50363,0.11162,0.0094],"force_p95":0.60925,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55189,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50353,0.16965,0.17018]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49989,0.19979,0.29909]}],"total_contact_groups":9},"final_pose_error":0.07273,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5073,-0.07004,0.03694],"final_tcp_position":[0.49145,-0.04344,0.02954],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":11.3594,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":870.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.03393],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":1.39455,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":864.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50861,0.14128,0.04853],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49318,0.05823,0.03479],"object_pos_start":[0.50372,0.11175,0.03393],"object_to_goal_dist_end":0.1385,"object_to_goal_dist_start":0.19188,"object_z_max":0.03577,"peak_contact_force":1.62142,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2273.0,"raw_peak_contact_force":11.3594,"subtask_id":"contact_peg","tcp_end":[0.50094,0.08715,0.03258],"tcp_start":[0.50861,0.14128,0.04853],"tcp_to_object_dist_end":0.03003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5073,-0.07004,0.03694],"object_pos_start":[0.49318,0.05823,0.03479],"object_to_goal_dist_end":0.01272,"object_to_goal_dist_start":0.1385,"object_z_max":0.03704,"peak_contact_force":9.95806,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1775.0,"raw_peak_contact_force":10.52305,"subtask_id":"push_through","tcp_end":[0.49145,-0.04344,0.02954],"tcp_start":[0.50094,0.08715,0.03258],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01117,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.05236,"approach_behind.target_x_offset":0.0017,"approach_behind.target_y_offset":0.03253,"engage_peg.contact_distance":0.03664,"engage_peg.contact_speed":0.03084,"push_channel.lateral_offset_x":0.00657,"push_channel.push_distance":0.17256,"push_channel.push_duration":11.21485,"push_channel.push_speed":0.05401},"optimized_scores":{"best_composite_score":0.0724,"best_fitness_score":0.5524,"best_task_score":0.3826},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":81.0,"contact_point_centroid":[0.475,0.12,0.04063],"force_p95":18.81649,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":20.94443,"mean_force":13.67633,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.48629,0.12301,0.03829]},{"body_a":"peg","body_b":"channel_base_body","contact_count":768.0,"contact_point_centroid":[0.50704,0.02174,0.00994],"force_p95":17.53793,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.43433,"mean_force":7.67253,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4905,0.06169,0.03018]},{"body_a":"attachment","body_b":"peg","contact_count":936.0,"contact_point_centroid":[0.49841,0.04837,0.03675],"force_p95":14.0213,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.39849,"mean_force":6.31335,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49087,0.05847,0.03021]},{"body_a":"attachment","body_b":"peg","contact_count":865.0,"contact_point_centroid":[0.49424,0.11316,0.04407],"force_p95":14.50129,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.64127,"mean_force":5.64948,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.48604,0.12277,0.03813]},{"body_a":"peg","body_b":"link7","contact_count":361.0,"contact_point_centroid":[0.52039,0.0676,0.06417],"force_p95":15.0682,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.52607,"mean_force":8.59046,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48788,0.08445,0.02991]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":441.0,"contact_point_centroid":[0.52525,0.09038,0.03386],"force_p95":13.22962,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.13871,"mean_force":7.18567,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.48762,0.11199,0.03553]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":854.0,"contact_point_centroid":[0.52511,0.0313,0.03505],"force_p95":10.57122,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.7437,"mean_force":4.14769,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49095,0.05704,0.03015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":918.0,"contact_point_centroid":[0.50563,0.08807,0.00992],"force_p95":5.8427,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.26599,"mean_force":3.29863,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"contact","tcp_position_centroid":[0.4857,0.12575,0.03895]},{"body_a":"peg","body_b":"channel_base_body","contact_count":818.0,"contact_point_centroid":[0.49616,0.11916,0.00942],"force_p95":0.60747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55051,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49154,0.17556,0.17013]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49969,0.19962,0.29786]}],"total_contact_groups":10},"final_pose_error":0.11014,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,-0.01622,0.03603],"final_tcp_position":[0.49655,0.01226,0.03119],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":20.94443,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.12119,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.20132,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5152,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":842.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48503,0.1531,0.04937],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50774,0.0764,0.039],"object_pos_start":[0.49605,0.12119,0.03384],"object_to_goal_dist_end":0.1566,"object_to_goal_dist_start":0.20132,"object_z_max":0.03898,"peak_contact_force":7.16717,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2305.0,"raw_peak_contact_force":20.94443,"subtask_id":"contact_peg","tcp_end":[0.48896,0.10155,0.03295],"tcp_start":[0.48503,0.1531,0.04937],"tcp_to_object_dist_end":0.03196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.01622,0.03603],"object_pos_start":[0.50774,0.0764,0.039],"object_to_goal_dist_end":0.06428,"object_to_goal_dist_start":0.1566,"object_z_max":0.03902,"peak_contact_force":3.30928,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2919.0,"raw_peak_contact_force":19.43433,"subtask_id":"push_through","tcp_end":[0.49655,0.01226,0.03119],"tcp_start":[0.48896,0.10155,0.03295],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```