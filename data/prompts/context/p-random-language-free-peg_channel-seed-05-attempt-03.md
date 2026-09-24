## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4640 | 0.82 | ✅ accepted |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0477 | 0.49 | ✅ accepted |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | -0.1612 | 0.00 | ✅ accepted |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.820, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=0.464) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push_approach
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.0
  weight: 0.3
- id: push_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind_high
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.08
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push_approach
- id: descend_to_lateral
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.08
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push_approach
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
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
    force_limit:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 40.0
      binds_to:
      - path: guards.force_safe.threshold
        mode: replace
    lateral_nudge:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_safe
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_channel
- id: retract_upward
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_lateral** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_safe.threshold (replace)
    - lateral_nudge: status=consumed; consumers=retry.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safe, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_upward** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=peg, offset=[0.0, 0.0, 0.1], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.464
- **task_score** (E): 0.820
- **fitness_score**: 0.874  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_high | 1.00 | 1.00 | 0.1549 |
| descend_to_lateral | 1.00 | 1.00 | 0.1121 |
| push_along_channel | 0.00 | 1.00 | 0.0002 |
| retract_upward | 1.00 | 1.00 | 0.0644 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.176, 0.149) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.544 | 2.488 |
| descend_to_lateral | descend | 1.00 / step_budget | (0.508, 0.176, 0.149)→(0.501, 0.173, 0.037) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.537 | 0.589 |
| push_along_channel | push | 0.00 / guard_failure | (0.500, -0.053, 0.030)→(0.500, -0.053, 0.030) | (0.504, 0.095, 0.034)→(0.504, -0.082, 0.036) | 0.175→0.006 | 1.00 / 2.000 | 0.496 | 49.250 |
| retract_upward | retract | 1.00 / step_budget | (0.500, -0.053, 0.030)→(0.497, -0.064, 0.093) | (0.504, -0.082, 0.036)→(0.504, -0.073, 0.068) | 0.007→0.030 | 1.00 / 1.000 | 0.421 | 103.917 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.915
- phase_breakdown.pre_push_approach_score: 0.810
- phase_breakdown.push_channel_score: 0.959

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.949
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.514
- **K-run variance**: 0.0079
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.294


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03846,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.07947,"descend_to_lateral.descend_speed":0.02528,"push_along_channel.force_limit":41.11808,"push_along_channel.lateral_nudge":0.01138,"push_along_channel.push_distance":0.20067,"push_along_channel.push_speed":0.05617,"retract_upward.retract_speed":0.07857},"optimized_scores":{"best_composite_score":0.3387,"best_fitness_score":0.7487,"best_task_score":0.56354},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":66.0,"contact_point_centroid":[0.50209,-0.06597,0.05753],"force_p95":99.48809,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.19057,"mean_force":56.31961,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49802,-0.0551,0.05519]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.50619,-0.10091,0.05753],"force_p95":85.44738,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.44336,"mean_force":45.34393,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49827,-0.05494,0.05359]},{"body_a":"attachment","body_b":"peg","contact_count":337.0,"contact_point_centroid":[0.50473,0.0352,0.04704],"force_p95":23.44769,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.7685,"mean_force":7.12843,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50074,0.04687,0.03107]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.5039,-0.10078,0.05943],"force_p95":39.60862,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.86165,"mean_force":24.54117,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50167,-0.04957,0.02963]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":326.0,"contact_point_centroid":[0.52519,0.01798,0.03534],"force_p95":20.24684,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.82837,"mean_force":4.56406,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50073,0.0474,0.03107]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.52518,-0.08396,0.05996],"force_p95":27.66882,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.44572,"mean_force":16.32344,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49748,-0.05547,0.05895]},{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.50967,-0.09037,0.0097],"force_p95":24.97564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.12234,"mean_force":6.77583,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49888,-0.05275,0.03566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":309.0,"contact_point_centroid":[0.50477,0.03347,0.00957],"force_p95":18.15465,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.10959,"mean_force":3.99608,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50088,0.08108,0.03212]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47474,-0.06411,0.0383],"force_p95":22.61603,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.14405,"mean_force":11.93567,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49745,-0.05705,0.07248]},{"body_a":"peg","body_b":"channel_base_body","contact_count":459.0,"contact_point_centroid":[0.50561,0.10457,0.00937],"force_p95":0.57873,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57099,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.50919,0.19179,0.22019]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.50001,0.19932,0.29652]},{"body_a":"peg","body_b":"channel_base_body","contact_count":576.0,"contact_point_centroid":[0.5058,0.1047,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57678,"mean_force":0.54629,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.51005,0.18361,0.09201]}],"total_contact_groups":12},"final_pose_error":0.04966,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50793,-0.06734,0.06418],"final_tcp_position":[0.49817,-0.06422,0.09295],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":100.19057,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55203,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":491.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_push_approach","tcp_end":[0.51928,0.18486,0.14833],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.10472,0.03383],"object_pos_start":[0.50583,0.10463,0.03383],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18483,"object_z_max":0.03384,"peak_contact_force":0.52968,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":576.0,"raw_peak_contact_force":0.57678,"subtask_id":"pre_push_approach","tcp_end":[0.50306,0.18328,0.03775],"tcp_start":[0.51928,0.18486,0.14833],"tcp_to_object_dist_end":0.07871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.50547,-0.08065,0.03742],"object_pos_start":[0.50593,0.10472,0.03383],"object_to_goal_dist_end":0.00608,"object_to_goal_dist_start":0.18492,"object_z_max":0.03752,"peak_contact_force":0.1838,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":980.0,"raw_peak_contact_force":43.7685,"subtask_id":"push_channel","tcp_end":[0.50159,-0.05074,0.02949],"tcp_start":[0.50164,-0.05059,0.02955],"tcp_to_object_dist_end":0.03119,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":87.0,"n_steps_budget":930.0,"object_pos_end":[0.50793,-0.06734,0.06418],"object_pos_start":[0.50547,-0.08092,0.03744],"object_to_goal_dist_end":0.02842,"object_to_goal_dist_start":0.00611,"object_z_max":0.06395,"peak_contact_force":0.96256,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":207.0,"raw_peak_contact_force":100.19057,"tcp_end":[0.49817,-0.06422,0.09295],"tcp_start":[0.50159,-0.05074,0.02949],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77926,"average_solve_count":299.0,"average_success_count":299.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.04801,"descend_to_lateral.descend_speed":0.02098,"push_along_channel.force_limit":39.80133,"push_along_channel.lateral_nudge":0.01116,"push_along_channel.push_distance":0.22881,"push_along_channel.push_speed":0.05418,"retract_upward.retract_speed":0.0762},"optimized_scores":{"best_composite_score":0.51447,"best_fitness_score":0.92447,"best_task_score":0.89582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":88.0,"contact_point_centroid":[0.49693,-0.06697,0.05681],"force_p95":105.33013,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.16406,"mean_force":65.50509,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49495,-0.0559,0.05475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.49915,-0.1009,0.06089],"force_p95":105.13678,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.05978,"mean_force":63.30173,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.495,-0.05614,0.05596]},{"body_a":"attachment","body_b":"peg","contact_count":267.0,"contact_point_centroid":[0.5001,0.00309,0.04096],"force_p95":13.21387,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.47734,"mean_force":2.45334,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49718,0.01481,0.03075]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50006,-0.10035,0.05391],"force_p95":47.14065,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.27346,"mean_force":28.86859,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49803,-0.05283,0.03007]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.50294,0.01677,0.00957],"force_p95":9.22066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.96606,"mean_force":2.04011,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49701,0.06275,0.03176]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52518,0.03465,0.05974],"force_p95":13.25889,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.3628,"mean_force":1.63603,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4966,0.06449,0.03124]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.503,0.06746,0.00934],"force_p95":0.55734,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56342,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49911,0.17499,0.22206]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47495,-0.07261,0.03242],"force_p95":1.34834,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35927,"mean_force":1.24989,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49446,-0.05576,0.06609]},{"body_a":"peg","body_b":"channel_base_body","contact_count":693.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55092,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.49811,0.14844,0.09078]}],"total_contact_groups":9},"final_pose_error":0.04969,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50023,-0.07587,0.07066],"final_tcp_position":[0.49673,-0.0636,0.09321],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":106.16406,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55065,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":513.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push_approach","tcp_end":[0.49987,0.15103,0.14859],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50307,0.0675,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.55056,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":693.0,"raw_peak_contact_force":0.55092,"subtask_id":"pre_push_approach","tcp_end":[0.499,0.14663,0.0365],"tcp_start":[0.49987,0.15103,0.14859],"tcp_to_object_dist_end":0.07928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50063,-0.08288,0.03547],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.0054,"object_to_goal_dist_start":0.14766,"object_z_max":0.03738,"peak_contact_force":0.76118,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":608.0,"raw_peak_contact_force":50.47734,"subtask_id":"push_channel","tcp_end":[0.49794,-0.05394,0.02993],"tcp_start":[0.49799,-0.05381,0.02999],"tcp_to_object_dist_end":0.02959,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":91.0,"n_steps_budget":930.0,"object_pos_end":[0.50023,-0.07587,0.07066],"object_pos_start":[0.50051,-0.08321,0.03549],"object_to_goal_dist_end":0.03094,"object_to_goal_dist_start":0.00556,"object_z_max":0.07021,"peak_contact_force":0.15555,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":181.0,"raw_peak_contact_force":106.16406,"tcp_end":[0.49673,-0.0636,0.09321],"tcp_start":[0.49794,-0.05394,0.02993],"tcp_to_object_dist_end":0.02591,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22441,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.04552,"descend_to_lateral.descend_speed":0.02889,"push_along_channel.force_limit":47.6044,"push_along_channel.lateral_nudge":0.01397,"push_along_channel.push_distance":0.21421,"push_along_channel.push_speed":0.07663,"retract_upward.retract_speed":0.08542},"optimized_scores":{"best_composite_score":0.53875,"best_fitness_score":0.94875,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":86.0,"contact_point_centroid":[0.50063,-0.06714,0.05763],"force_p95":101.16934,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.39541,"mean_force":63.9818,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49551,-0.05689,0.05377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.50774,-0.10086,0.06356],"force_p95":100.80855,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.16678,"mean_force":59.75482,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49556,-0.05726,0.05578]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.50595,-0.1002,0.05534],"force_p95":52.80428,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.50334,"mean_force":24.52149,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4994,-0.05286,0.02958]},{"body_a":"attachment","body_b":"peg","contact_count":387.0,"contact_point_centroid":[0.50338,0.03574,0.04948],"force_p95":39.93341,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.39184,"mean_force":10.13739,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49792,0.04718,0.03054]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":342.0,"contact_point_centroid":[0.52537,0.00906,0.03607],"force_p95":33.63085,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.25474,"mean_force":8.8457,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49794,0.03771,0.03041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":283.0,"contact_point_centroid":[0.50528,0.04306,0.00964],"force_p95":18.08452,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.70932,"mean_force":4.14467,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.498,0.09204,0.0317]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52508,-0.08353,0.05999],"force_p95":17.26877,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.68971,"mean_force":8.15976,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49453,-0.05662,0.06188]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47493,-0.07032,0.04606],"force_p95":7.47599,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.53543,"mean_force":6.5949,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49536,-0.05906,0.07645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":480.0,"contact_point_centroid":[0.50351,0.11167,0.00938],"force_p95":0.6125,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55979,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.50232,0.19516,0.2217]},{"body_a":"peg","body_b":"channel_base_body","contact_count":625.0,"contact_point_centroid":[0.50369,0.11162,0.00941],"force_p95":0.59927,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63902,"mean_force":0.54407,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.50187,0.19036,0.09146]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49978,0.19957,0.2991]}],"total_contact_groups":11},"final_pose_error":0.04964,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50531,-0.07462,0.06942],"final_tcp_position":[0.49645,-0.06466,0.09293],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":105.39541,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11174,0.03385],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52834,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":496.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push_approach","tcp_end":[0.5062,0.1914,0.14916],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11173,0.03386],"object_pos_start":[0.50371,0.11174,0.03385],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19187,"object_z_max":0.03398,"peak_contact_force":0.53008,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":625.0,"raw_peak_contact_force":0.63902,"subtask_id":"pre_push_approach","tcp_end":[0.50006,0.19029,0.03691],"tcp_start":[0.5062,0.1914,0.14916],"tcp_to_object_dist_end":0.07871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":617.0,"n_steps_budget":1000.0,"object_pos_end":[0.50606,-0.08253,0.03577],"object_pos_start":[0.50371,0.11173,0.03386],"object_to_goal_dist_end":0.00781,"object_to_goal_dist_start":0.19186,"object_z_max":0.0374,"peak_contact_force":0.54323,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1023.0,"raw_peak_contact_force":53.50334,"subtask_id":"push_channel","tcp_end":[0.49933,-0.05507,0.02943],"tcp_start":[0.49937,-0.05491,0.02947],"tcp_to_object_dist_end":0.02897,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":91.0,"n_steps_budget":840.0,"object_pos_end":[0.50531,-0.07462,0.06942],"object_pos_start":[0.50613,-0.0829,0.03571],"object_to_goal_dist_end":0.03038,"object_to_goal_dist_start":0.00802,"object_z_max":0.06898,"peak_contact_force":0.14577,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":196.0,"raw_peak_contact_force":105.39541,"tcp_end":[0.49645,-0.06466,0.09293],"tcp_start":[0.49933,-0.05507,0.02943],"tcp_to_object_dist_end":0.02702,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```