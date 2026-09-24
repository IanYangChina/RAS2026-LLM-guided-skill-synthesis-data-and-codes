## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5102 | 0.81 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1186 | 0.34 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4067 | 0.80 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4627 | 0.82 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4640 | 0.82 | ✅ accepted |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.821, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.510) — your mutation base

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

- **Composite score**: 0.510
- **task_score** (E): 0.808
- **fitness_score**: 0.870  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_high | 1.00 | 1.00 | 0.1549 |
| descend_to_lateral | 1.00 | 1.00 | 0.1122 |
| push_along_channel | 0.00 | 1.00 | 0.0002 |
| retract_upward | 1.00 | 0.67 | 0.0595 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.176, 0.149) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.542 | 2.488 |
| descend_to_lateral | descend | 1.00 / step_budget | (0.508, 0.176, 0.149)→(0.501, 0.173, 0.037) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.537 | 0.585 |
| push_along_channel | push | 0.00 / guard_failure | (0.496, -0.053, 0.035)→(0.496, -0.053, 0.035) | (0.504, 0.095, 0.034)→(0.506, -0.081, 0.038) | 0.175→0.006 | 1.00 / 2.667 | 1.530 | 50.198 |
| retract_upward | retract | 1.00 / step_budget | (0.496, -0.053, 0.035)→(0.496, -0.064, 0.093) | (0.506, -0.081, 0.038)→(0.505, -0.071, 0.069) | 0.006→0.031 | 0.67 / 0.667 | 0.091 | 97.722 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.917
- phase_breakdown.pre_push_approach_score: 0.810
- phase_breakdown.push_channel_score: 0.962

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.950
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.552
- **K-run variance**: 0.0076
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.249


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94483,"average_solve_count":290.0,"average_success_count":290.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.04529,"descend_to_lateral.descend_speed":0.02473,"push_along_channel.force_limit":36.13125,"push_along_channel.lateral_nudge":0.01564,"push_along_channel.push_speed":0.06192,"retract_upward.retract_speed":0.06403},"optimized_scores":{"best_composite_score":0.38903,"best_fitness_score":0.74903,"best_task_score":0.57469},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":79.0,"contact_point_centroid":[0.49953,-0.06677,0.05997],"force_p95":99.41766,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.43206,"mean_force":56.60692,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49418,-0.05657,0.05667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":85.0,"contact_point_centroid":[0.50817,-0.10079,0.06354],"force_p95":99.10852,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.05761,"mean_force":52.65073,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49428,-0.05706,0.05906]},{"body_a":"attachment","body_b":"peg","contact_count":384.0,"contact_point_centroid":[0.50282,0.02442,0.04854],"force_p95":26.97413,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.82236,"mean_force":7.49547,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49765,0.03582,0.03419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50739,-0.10016,0.06119],"force_p95":35.05204,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.22708,"mean_force":23.99898,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49646,-0.05367,0.03492]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":356.0,"contact_point_centroid":[0.52527,0.00669,0.03264],"force_p95":26.74093,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.84476,"mean_force":5.90948,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49761,0.0348,0.03419]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52509,-0.08354,0.05092],"force_p95":26.11525,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.8257,"mean_force":7.50823,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49456,-0.05538,0.0499]},{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.50599,0.0474,0.00962],"force_p95":18.72233,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.83711,"mean_force":4.35009,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49902,0.09706,0.03432]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47468,-0.0732,0.03471],"force_p95":13.93299,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.4561,"mean_force":6.14868,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49353,-0.0567,0.06603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":492.0,"contact_point_centroid":[0.50559,0.10471,0.00937],"force_p95":0.57756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56934,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.50905,0.19179,0.22048]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49991,0.19933,0.29684]},{"body_a":"peg","body_b":"channel_base_body","contact_count":577.0,"contact_point_centroid":[0.50595,0.10454,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57647,"mean_force":0.54632,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.51013,0.18363,0.09199]}],"total_contact_groups":11},"final_pose_error":0.04921,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50832,-0.07129,0.06906],"final_tcp_position":[0.49582,-0.06462,0.09344],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":100.43206,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54158,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":524.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_push_approach","tcp_end":[0.51931,0.18489,0.14842],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10459,0.03384],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":0.55187,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":577.0,"raw_peak_contact_force":0.57647,"subtask_id":"pre_push_approach","tcp_end":[0.5032,0.18329,0.03762],"tcp_start":[0.51931,0.18489,0.14842],"tcp_to_object_dist_end":0.07883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.50729,-0.08134,0.03692],"object_pos_start":[0.50584,0.10459,0.03384],"object_to_goal_dist_end":0.00802,"object_to_goal_dist_start":0.18478,"object_z_max":0.03726,"peak_contact_force":3.29319,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1002.0,"raw_peak_contact_force":43.82236,"subtask_id":"push_channel","tcp_end":[0.49636,-0.05411,0.03484],"tcp_start":[0.49642,-0.05394,0.03489],"tcp_to_object_dist_end":0.02941,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.50832,-0.07129,0.06906],"object_pos_start":[0.50734,-0.08187,0.03683],"object_to_goal_dist_end":0.03146,"object_to_goal_dist_start":0.00821,"object_z_max":0.06859,"peak_contact_force":0.136,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":186.0,"raw_peak_contact_force":100.43206,"tcp_end":[0.49582,-0.06462,0.09344],"tcp_start":[0.49636,-0.05411,0.03484],"tcp_to_object_dist_end":0.0282,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91259,"average_solve_count":286.0,"average_success_count":286.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.04416,"descend_to_lateral.descend_speed":0.02497,"push_along_channel.force_limit":44.00684,"push_along_channel.lateral_nudge":0.00782,"push_along_channel.push_speed":0.06333,"retract_upward.retract_speed":0.05401},"optimized_scores":{"best_composite_score":0.55174,"best_fitness_score":0.91174,"best_task_score":0.85028},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":72.0,"contact_point_centroid":[0.49842,-0.06425,0.05671],"force_p95":93.18138,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.82432,"mean_force":54.07992,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49511,-0.05323,0.05717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.50033,-0.10079,0.06193],"force_p95":93.08098,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.68995,"mean_force":48.59313,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49515,-0.05331,0.05705]},{"body_a":"attachment","body_b":"peg","contact_count":157.0,"contact_point_centroid":[0.49825,0.01243,0.0412],"force_p95":12.50974,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.55136,"mean_force":3.93174,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49607,0.02403,0.03383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49897,-0.10051,0.05918],"force_p95":42.04151,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.10394,"mean_force":20.89939,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49634,-0.04842,0.0349]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.50103,0.01613,0.00945],"force_p95":10.97521,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.33222,"mean_force":2.1632,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49632,0.06079,0.0338]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":55.0,"contact_point_centroid":[0.47464,-0.02867,0.04092],"force_p95":4.60994,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.09624,"mean_force":1.31981,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49612,0.00308,0.03414]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.49412,-0.08702,0.00998],"force_p95":6.66995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.2169,"mean_force":3.07951,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49536,-0.05009,0.03593]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":39.0,"contact_point_centroid":[0.5251,-0.02047,0.03047],"force_p95":3.8542,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.4174,"mean_force":0.91278,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49614,0.00967,0.03405]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47489,-0.06209,0.03676],"force_p95":2.49633,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.5216,"mean_force":2.20748,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49533,-0.05481,0.07163]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.503,0.06746,0.00934],"force_p95":0.55734,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56342,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49911,0.17502,0.22214]},{"body_a":"peg","body_b":"channel_base_body","contact_count":677.0,"contact_point_centroid":[0.50309,0.06749,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55092,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.49812,0.14844,0.09072]}],"total_contact_groups":11},"final_pose_error":0.04968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50213,-0.06858,0.06797],"final_tcp_position":[0.49685,-0.0628,0.0935],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":93.82432,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55065,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":513.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push_approach","tcp_end":[0.49987,0.15102,0.14855],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50307,0.0675,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.5435,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":677.0,"raw_peak_contact_force":0.55092,"subtask_id":"pre_push_approach","tcp_end":[0.499,0.14663,0.03645],"tcp_start":[0.49987,0.15102,0.14855],"tcp_to_object_dist_end":0.07932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.50291,-0.0786,0.03882],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.00344,"object_to_goal_dist_start":0.14762,"object_z_max":0.0428,"peak_contact_force":0.63388,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":573.0,"raw_peak_contact_force":50.55136,"subtask_id":"push_channel","tcp_end":[0.49627,-0.04961,0.03482],"tcp_start":[0.49631,-0.04947,0.03486],"tcp_to_object_dist_end":0.03002,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.50213,-0.06858,0.06797],"object_pos_start":[0.50294,-0.07879,0.03884],"object_to_goal_dist_end":0.03028,"object_to_goal_dist_start":0.00339,"object_z_max":0.06767,"peak_contact_force":0.0,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":169.0,"raw_peak_contact_force":93.82432,"tcp_end":[0.49685,-0.0628,0.0935],"tcp_start":[0.49627,-0.04961,0.03482],"tcp_to_object_dist_end":0.02671,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93502,"average_solve_count":277.0,"average_success_count":277.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_high.approach_speed":0.05184,"descend_to_lateral.descend_speed":0.02014,"push_along_channel.force_limit":45.43831,"push_along_channel.lateral_nudge":0.0097,"push_along_channel.push_speed":0.08127,"retract_upward.retract_speed":0.08067},"optimized_scores":{"best_composite_score":0.58998,"best_fitness_score":0.94998,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":78.0,"contact_point_centroid":[0.49948,-0.06737,0.06068],"force_p95":97.8127,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.9091,"mean_force":57.49823,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49367,-0.05738,0.05693]},{"body_a":"peg","body_b":"channel_base_body","contact_count":83.0,"contact_point_centroid":[0.5084,-0.10081,0.06401],"force_p95":97.45263,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.4344,"mean_force":52.98537,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49376,-0.05777,0.05893]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50622,-0.10032,0.06226],"force_p95":55.67433,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.22072,"mean_force":38.57386,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49633,-0.05455,0.03497]},{"body_a":"attachment","body_b":"peg","contact_count":354.0,"contact_point_centroid":[0.50206,0.03099,0.04977],"force_p95":36.40609,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.74321,"mean_force":9.84714,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49619,0.04223,0.03376]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":346.0,"contact_point_centroid":[0.5253,0.00531,0.03344],"force_p95":34.47028,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.44671,"mean_force":7.44685,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49612,0.03293,0.03385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.50503,0.05086,0.00957],"force_p95":20.26782,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.1486,"mean_force":4.70797,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49687,0.09995,0.03379]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52508,-0.0837,0.05998],"force_p95":18.11574,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.48875,"mean_force":9.34306,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49285,-0.05709,0.06241]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.4749,-0.07113,0.04075],"force_p95":5.69626,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.74066,"mean_force":5.19694,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49346,-0.05845,0.07216]},{"body_a":"peg","body_b":"channel_base_body","contact_count":478.0,"contact_point_centroid":[0.50355,0.11167,0.00936],"force_p95":0.61648,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56114,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.50232,0.19515,0.22157]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.50367,0.11177,0.00939],"force_p95":0.61872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62617,"mean_force":0.54468,"phase_index":1.0,"phase_name":"descend_to_lateral","phase_type":"descend","tcp_position_centroid":[0.50185,0.19038,0.09145]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_high","phase_type":"approach","tcp_position_centroid":[0.49979,0.19957,0.29904]}],"total_contact_groups":11},"final_pose_error":0.04971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,-0.07285,0.06908],"final_tcp_position":[0.49539,-0.06489,0.09287],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":98.9091,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11178,0.03386],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53522,"phase_name":"approach_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":494.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push_approach","tcp_end":[0.5062,0.1914,0.14919],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11171,0.03382],"object_pos_start":[0.5037,0.11178,0.03386],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19191,"object_z_max":0.03397,"peak_contact_force":0.51579,"phase_name":"descend_to_lateral","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":655.0,"raw_peak_contact_force":0.62617,"subtask_id":"pre_push_approach","tcp_end":[0.50005,0.19033,0.03683],"tcp_start":[0.5062,0.1914,0.14919],"tcp_to_object_dist_end":0.07876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.50648,-0.08218,0.03773],"object_pos_start":[0.50375,0.11171,0.03382],"object_to_goal_dist_end":0.0072,"object_to_goal_dist_start":0.19185,"object_z_max":0.03801,"peak_contact_force":0.66298,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":972.0,"raw_peak_contact_force":56.22072,"subtask_id":"push_channel","tcp_end":[0.49626,-0.05513,0.03491],"tcp_start":[0.49631,-0.05497,0.03495],"tcp_to_object_dist_end":0.02905,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":83.0,"n_steps_budget":840.0,"object_pos_end":[0.50587,-0.07285,0.06908],"object_pos_start":[0.50642,-0.08268,0.03766],"object_to_goal_dist_end":0.03052,"object_to_goal_dist_start":0.00734,"object_z_max":0.0686,"peak_contact_force":0.13841,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":183.0,"raw_peak_contact_force":98.9091,"tcp_end":[0.49539,-0.06489,0.09287],"tcp_start":[0.49626,-0.05513,0.03491],"tcp_to_object_dist_end":0.02718,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```