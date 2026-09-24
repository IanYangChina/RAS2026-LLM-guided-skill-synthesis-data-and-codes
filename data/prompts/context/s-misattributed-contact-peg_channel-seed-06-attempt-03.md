## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.5222 | 0.76 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5658 | 0.83 | ✅ accepted |
| 1 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0775 | 0.00 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.827, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.522) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.1
  weight: 0.3
- id: reach_contact
  anchor: object
  weight: 0.3
- id: reach_goal
  metric: goal_progress
  weight: 0.4
phases:
- id: approach_1
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
    - 0.03
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_1
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
    - 0.03
    - -0.005
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: impedance_motion
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard_push
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: reach_goal
- id: retract_1
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
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, -0.005], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard_push, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.522
- **task_score** (E): 0.760
- **fitness_score**: 0.737  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.356
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1672 |
| descend_1 | 1.00 | 1.00 | 0.1167 |
| contact_1 | 1.00 | 1.00 | 0.0026 |
| lateral_adjust | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.67 | 1.00 | 0.1418 |
| retract_1 | 1.00 | 1.00 | 0.0604 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.134, 0.148) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.333 | 0.802 | 5.341 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.134, 0.148)→(0.497, 0.129, 0.032) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.035) | 0.180→0.179 | 1.00 / 2.000 | 5.817 | 5.916 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.129, 0.032)→(0.496, 0.127, 0.030) | (0.501, 0.099, 0.035)→(0.501, 0.098, 0.035) | 0.179→0.178 | 1.00 / 2.000 | 8.137 | 8.137 |
| lateral_adjust | push | 1.00 / force_exceeded | (0.496, 0.127, 0.030)→(0.496, 0.127, 0.030) | (0.501, 0.098, 0.035)→(0.501, 0.098, 0.035) | 0.178→0.178 | 1.00 / 2.667 | 10.933 | 47.940 |
| push_1 | push | 0.67 / step_budget | (0.496, 0.127, 0.030)→(0.492, -0.014, 0.026) | (0.501, 0.098, 0.035)→(0.506, -0.041, 0.036) | 0.178→0.042 | 1.00 / 1.000 | 0.542 | 136.478 |
| retract_1 | retract | 1.00 / step_budget | (0.491, 0.005, 0.026)→(0.488, 0.004, 0.086) | (0.506, -0.022, 0.036)→(0.505, -0.023, 0.034) | 0.059→0.058 | 1.00 / 1.000 | 0.552 | 2.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.924
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.924
- phase_score: 0.786
- phase_breakdown.reach_pre_contact_score: 0.820
- phase_breakdown.reach_contact_score: 0.539
- phase_breakdown.reach_goal_score: 0.947

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.841
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.937
- **Median Q (composite search score)**: 0.565
- **K-run variance**: 0.0203
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.245


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87549,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06565,"contact_1.force_threshold":5.39437,"contact_1.speed":0.01063,"descend_1.speed":0.03477,"lateral_adjust.lat_force_threshold":7.36922,"lateral_adjust.lat_speed":0.0108,"push_1.push_distance":0.17298,"push_1.push_speed":0.02036,"retract_1.speed":0.05339},"optimized_scores":{"best_composite_score":0.67129,"best_fitness_score":0.84129,"best_task_score":0.92351},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54848,-0.1,0.065],"force_p95":69.47549,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.47549,"mean_force":69.47549,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49446,-0.05208,0.02592]},{"body_a":"attachment","body_b":"peg","contact_count":303.0,"contact_point_centroid":[0.50097,0.00785,0.04204],"force_p95":17.8397,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.73004,"mean_force":4.51058,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49458,0.0191,0.02623]},{"body_a":"peg","body_b":"channel_base_body","contact_count":158.0,"contact_point_centroid":[0.50614,-0.02206,0.00988],"force_p95":22.46735,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.62757,"mean_force":8.81241,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49474,0.02234,0.02643]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":220.0,"contact_point_centroid":[0.52518,0.00026,0.02844],"force_p95":11.43147,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.99294,"mean_force":2.22945,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49451,0.02779,0.02614]},{"body_a":"peg","body_b":"link7","contact_count":108.0,"contact_point_centroid":[0.52132,-0.03225,0.06218],"force_p95":11.22407,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.51331,"mean_force":2.84178,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4943,-0.0125,0.02584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50975,0.05049,0.00987],"force_p95":7.41845,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.41845,"mean_force":7.41845,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49789,0.09639,0.03036]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50159,0.08439,0.04691],"force_p95":7.17737,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.17737,"mean_force":7.17737,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49789,0.09639,0.03036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":679.0,"contact_point_centroid":[0.50304,0.06637,0.0094],"force_p95":0.55072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.47255,"mean_force":0.58373,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49804,0.10036,0.08732]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.4966,0.05184,0.00986],"force_p95":3.6136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.44922,"mean_force":1.2565,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49841,0.0969,0.03097]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50215,0.08478,0.05289],"force_p95":4.61627,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.13852,"mean_force":2.63169,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49836,0.09687,0.03092]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50254,0.08531,0.05906],"force_p95":4.50123,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.09649,"mean_force":2.05845,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49883,0.0974,0.03636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":590.0,"contact_point_centroid":[0.5031,0.06744,0.00934],"force_p95":0.55521,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49904,0.15123,0.22058]}],"total_contact_groups":12},"final_pose_error":0.02485,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50688,-0.0803,0.03646],"final_tcp_position":[0.49448,-0.05242,0.02593],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":69.47549,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":1.42667,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":694.0,"raw_peak_contact_force":5.47255,"subtask_id":"reach_pre_contact","tcp_end":[0.49982,0.10417,0.1466],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.50293,0.06716,0.03482],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14728,"object_to_goal_dist_start":0.14759,"object_z_max":0.03482,"peak_contact_force":5.44922,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20.0,"raw_peak_contact_force":5.44922,"subtask_id":"reach_contact","tcp_end":[0.49893,0.09715,0.03161],"tcp_start":[0.49982,0.10417,0.1466],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50326,0.06672,0.03511],"object_pos_start":[0.50293,0.06716,0.03482],"object_to_goal_dist_end":0.14684,"object_to_goal_dist_start":0.14728,"object_z_max":0.03509,"peak_contact_force":7.41845,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":7.41845,"subtask_id":"reach_contact","tcp_end":[0.49789,0.09639,0.03036],"tcp_start":[0.49893,0.09715,0.03161],"tcp_to_object_dist_end":0.03052,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":870.0,"object_pos_end":[0.5033,0.06664,0.03516],"object_pos_start":[0.50326,0.06672,0.03511],"object_to_goal_dist_end":0.14676,"object_to_goal_dist_start":0.14684,"object_z_max":0.03511,"peak_contact_force":0.00072,"phase_name":"lateral_adjust","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":790.0,"raw_peak_contact_force":69.47549,"subtask_id":"reach_contact","tcp_end":[0.49784,0.09633,0.03029],"tcp_start":[0.49789,0.09639,0.03036],"tcp_to_object_dist_end":0.03057,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.50688,-0.0803,0.03646],"object_pos_start":[0.5033,0.06664,0.03516],"object_to_goal_dist_end":0.00774,"object_to_goal_dist_start":0.14676,"object_z_max":0.03699,"peak_contact_force":0.54748,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":590.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_goal","tcp_end":[0.49448,-0.05242,0.02593],"tcp_start":[0.49784,0.09633,0.03029],"tcp_to_object_dist_end":0.03228,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81,"average_solve_count":300.0,"average_success_count":300.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06119,"contact_1.force_threshold":6.26011,"contact_1.speed":0.00986,"descend_1.speed":0.03155,"lateral_adjust.lat_force_threshold":7.58778,"lateral_adjust.lat_speed":0.01252,"push_1.push_distance":0.1667,"push_1.push_speed":0.01761,"retract_1.speed":0.05081},"optimized_scores":{"best_composite_score":0.56479,"best_fitness_score":0.80146,"best_task_score":0.93718},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":354.0,"contact_point_centroid":[0.50207,0.05319,0.04681],"force_p95":27.80074,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.85934,"mean_force":8.04142,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49542,0.06453,0.02634]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":277.0,"contact_point_centroid":[0.52526,0.03418,0.03745],"force_p95":26.33546,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.85332,"mean_force":8.00113,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49528,0.06217,0.02617]},{"body_a":"peg","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52264,0.00104,0.06206],"force_p95":24.4694,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.79336,"mean_force":5.48705,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49487,0.02001,0.02582]},{"body_a":"peg","body_b":"channel_base_body","contact_count":151.0,"contact_point_centroid":[0.50736,0.02133,0.00988],"force_p95":23.12899,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.30759,"mean_force":7.45539,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49549,0.06297,0.02647]},{"body_a":"peg","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.52011,-0.02939,0.06242],"force_p95":6.68955,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.52471,"mean_force":1.3382,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49416,-0.00851,0.02577]},{"body_a":"peg","body_b":"channel_base_body","contact_count":188.0,"contact_point_centroid":[0.50489,-0.04056,0.00947],"force_p95":0.78019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.13864,"mean_force":0.64778,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49178,-0.00796,0.05641]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50551,0.09301,0.00984],"force_p95":8.91205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.91205,"mean_force":8.91205,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49896,0.14028,0.03065]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50207,0.12828,0.04456],"force_p95":8.593,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.593,"mean_force":8.593,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.49896,0.14028,0.03065]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.50062,0.09553,0.00973],"force_p95":6.1379,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.04219,"mean_force":2.44989,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49949,0.14078,0.03129]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50265,0.12874,0.04787],"force_p95":6.25002,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.72035,"mean_force":3.87649,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4995,0.14077,0.03131]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50116,-0.01988,0.05665],"force_p95":2.66272,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.02817,"mean_force":0.66192,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49409,-0.00848,0.02592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.5037,0.10881,0.00946],"force_p95":0.75794,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.94331,"mean_force":0.64481,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50181,0.14297,0.0885]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.50299,0.12937,0.05763],"force_p95":4.98262,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.58472,"mean_force":2.13611,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50034,0.14139,0.04325]},{"body_a":"peg","body_b":"channel_base_body","contact_count":508.0,"contact_point_centroid":[0.50355,0.11167,0.00937],"force_p95":0.61193,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55985,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5023,0.172,0.2209]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49978,0.19934,0.29905]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.5253,-0.04048,0.05965],"force_p95":0.41559,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47261,"mean_force":0.1686,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49229,-0.00824,0.03711]}],"total_contact_groups":16},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50626,-0.03817,0.03393],"final_tcp_position":[0.4914,-0.00773,0.08602],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":37.85934,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11176,0.03376],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.49045,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":680.0,"raw_peak_contact_force":5.94331,"subtask_id":"reach_pre_contact","tcp_end":[0.50618,0.1457,0.14807],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.50388,0.11112,0.03463],"object_pos_start":[0.50373,0.11176,0.03376],"object_to_goal_dist_end":0.19124,"object_to_goal_dist_start":0.1919,"object_z_max":0.03474,"peak_contact_force":7.04219,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23.0,"raw_peak_contact_force":7.04219,"subtask_id":"reach_contact","tcp_end":[0.50003,0.14103,0.03198],"tcp_start":[0.50618,0.1457,0.14807],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50351,0.1105,0.03497],"object_pos_start":[0.50388,0.11112,0.03463],"object_to_goal_dist_end":0.19059,"object_to_goal_dist_start":0.19124,"object_z_max":0.03491,"peak_contact_force":8.91205,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":8.91205,"subtask_id":"reach_contact","tcp_end":[0.49896,0.14028,0.03065],"tcp_start":[0.50003,0.14103,0.03198],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.50354,0.1104,0.03504],"object_pos_start":[0.50351,0.1105,0.03497],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.19059,"object_z_max":0.03497,"peak_contact_force":2.91633,"phase_name":"lateral_adjust","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":805.0,"raw_peak_contact_force":37.85934,"subtask_id":"reach_contact","tcp_end":[0.49892,0.14021,0.03058],"tcp_start":[0.49896,0.14028,0.03065],"tcp_to_object_dist_end":0.03049,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.50568,-0.03568,0.03585],"object_pos_start":[0.50354,0.1104,0.03504],"object_to_goal_dist_end":0.04488,"object_to_goal_dist_start":0.1905,"object_z_max":0.03704,"peak_contact_force":0.54669,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":224.0,"raw_peak_contact_force":11.52471,"subtask_id":"reach_goal","tcp_end":[0.49456,-0.00774,0.02559],"tcp_start":[0.49892,0.14021,0.03058],"tcp_to_object_dist_end":0.03178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":200.0,"n_steps_budget":990.0,"object_pos_end":[0.50626,-0.03817,0.03393],"object_pos_start":[0.50568,-0.03568,0.03585],"object_to_goal_dist_end":0.04273,"object_to_goal_dist_start":0.04488,"object_z_max":0.03692,"peak_contact_force":0.54448,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":524.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.4914,-0.00773,0.08602],"tcp_start":[0.49456,-0.00774,0.02559],"tcp_to_object_dist_end":0.06214,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80565,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06526,"contact_1.force_threshold":4.85286,"contact_1.speed":0.01233,"descend_1.speed":0.03405,"lateral_adjust.lat_force_threshold":6.1853,"lateral_adjust.lat_speed":0.01149,"push_1.push_distance":0.14796,"push_1.push_speed":0.02628,"retract_1.speed":0.05249},"optimized_scores":{"best_composite_score":0.33056,"best_fitness_score":0.56723,"best_task_score":0.41984},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":62.0,"contact_point_centroid":[0.47498,0.0162,0.04419],"force_p95":256.21622,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":261.43129,"mean_force":152.60264,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48681,0.01624,0.04225]},{"body_a":"peg","body_b":"channel_base_body","contact_count":191.0,"contact_point_centroid":[0.50815,-0.017,0.00978],"force_p95":0.63943,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.97804,"mean_force":0.83069,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48629,0.0164,0.05518]},{"body_a":"peg","body_b":"channel_base_body","contact_count":337.0,"contact_point_centroid":[0.50628,0.03652,0.00996],"force_p95":31.5567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.48414,"mean_force":26.21359,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4875,0.07785,0.02575]},{"body_a":"peg","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.5193,0.00163,0.06165],"force_p95":21.68145,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.97592,"mean_force":6.79911,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48738,0.01633,0.02577]},{"body_a":"peg","body_b":"link7","contact_count":319.0,"contact_point_centroid":[0.51672,0.05468,0.06202],"force_p95":24.27826,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.00292,"mean_force":19.52313,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4874,0.07143,0.02563]},{"body_a":"attachment","body_b":"peg","contact_count":366.0,"contact_point_centroid":[0.49351,0.06971,0.02859],"force_p95":17.60023,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.85014,"mean_force":13.06611,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48751,0.07995,0.02577]},{"body_a":"attachment","body_b":"peg","contact_count":47.0,"contact_point_centroid":[0.49575,0.00597,0.05763],"force_p95":3.14659,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.9312,"mean_force":0.90841,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48692,0.01628,0.04094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49268,0.09861,0.00984],"force_p95":8.08037,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.08037,"mean_force":8.08037,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.48981,0.14535,0.02865]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49338,0.13344,0.04166],"force_p95":7.72728,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.72728,"mean_force":7.72728,"phase_index":3.0,"phase_name":"lateral_adjust","phase_type":"push","tcp_position_centroid":[0.48981,0.14535,0.02865]},{"body_a":"peg","body_b":"channel_base_body","contact_count":32.0,"contact_point_centroid":[0.49815,0.10169,0.0098],"force_p95":4.87333,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.25526,"mean_force":2.09712,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49058,0.14696,0.02964]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.49438,0.1348,0.04736],"force_p95":4.65552,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.81869,"mean_force":3.31219,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49043,0.14675,0.02945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":753.0,"contact_point_centroid":[0.49609,0.11614,0.00948],"force_p95":1.19829,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.60826,"mean_force":0.62456,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4868,0.14989,0.08767]},{"body_a":"attachment","body_b":"peg","contact_count":54.0,"contact_point_centroid":[0.4941,0.13652,0.05813],"force_p95":3.10824,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.23259,"mean_force":1.4639,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49055,0.14846,0.04289]},{"body_a":"peg","body_b":"channel_base_body","contact_count":477.0,"contact_point_centroid":[0.49629,0.11908,0.00945],"force_p95":0.61738,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55389,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49132,0.17533,0.221]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49948,0.19905,0.29783]}],"total_contact_groups":15},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50387,-0.00783,0.0338],"final_tcp_position":[0.48491,0.0167,0.086],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":261.43129,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11896,0.03395],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.48809,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":807.0,"raw_peak_contact_force":4.60826,"subtask_id":"reach_pre_contact","tcp_end":[0.48455,0.15254,0.14918],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.49595,0.11817,0.03483],"object_pos_start":[0.49608,0.11896,0.03395],"object_to_goal_dist_end":0.19828,"object_to_goal_dist_start":0.1991,"object_z_max":0.0349,"peak_contact_force":4.95943,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":48.0,"raw_peak_contact_force":5.25526,"subtask_id":"reach_contact","tcp_end":[0.4916,0.14811,0.03094],"tcp_start":[0.48455,0.15254,0.14918],"tcp_to_object_dist_end":0.0305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":36.0,"n_steps_budget":1000.0,"object_pos_end":[0.49571,0.11576,0.03508],"object_pos_start":[0.49595,0.11817,0.03483],"object_to_goal_dist_end":0.19587,"object_to_goal_dist_start":0.19828,"object_z_max":0.03545,"peak_contact_force":8.08037,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":8.08037,"subtask_id":"reach_contact","tcp_end":[0.48981,0.14535,0.02865],"tcp_start":[0.4916,0.14811,0.03094],"tcp_to_object_dist_end":0.03085,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":840.0,"object_pos_end":[0.49568,0.11569,0.03512],"object_pos_start":[0.49571,0.11576,0.03508],"object_to_goal_dist_end":0.1958,"object_to_goal_dist_start":0.19587,"object_z_max":0.03508,"peak_contact_force":29.88179,"phase_name":"lateral_adjust","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1022.0,"raw_peak_contact_force":36.48414,"subtask_id":"reach_contact","tcp_end":[0.48978,0.14529,0.0286],"tcp_start":[0.48981,0.14535,0.02865],"tcp_to_object_dist_end":0.03088,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50563,-0.00759,0.03654],"object_pos_start":[0.49568,0.11569,0.03512],"object_to_goal_dist_end":0.07271,"object_to_goal_dist_start":0.1958,"object_z_max":0.03714,"peak_contact_force":0.53801,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":309.0,"raw_peak_contact_force":261.43129,"subtask_id":"reach_goal","tcp_end":[0.4876,0.01688,0.02569],"tcp_start":[0.48978,0.14529,0.0286],"tcp_to_object_dist_end":0.03227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":194.0,"n_steps_budget":960.0,"object_pos_end":[0.50387,-0.00783,0.0338],"object_pos_start":[0.50563,-0.00759,0.03654],"object_to_goal_dist_end":0.07254,"object_to_goal_dist_start":0.07271,"object_z_max":0.03654,"peak_contact_force":0.56324,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":501.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48491,0.0167,0.086],"tcp_start":[0.4876,0.01688,0.02569],"tcp_to_object_dist_end":0.06071,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```