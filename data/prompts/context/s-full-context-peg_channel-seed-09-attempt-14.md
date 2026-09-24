## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0009 | 0.23 | ❌ rejected |
| 13 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | -0.1912 | 0.01 | ❌ rejected |
| 12 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.1988 | 0.25 | ❌ rejected |
| 11 | approach → descend → contact → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.1731 | 0.03 | ❌ rejected |
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0973 | 0.06 | ❌ rejected |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.001) — your mutation base

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

- **Composite score**: 0.001
- **task_score** (E): 0.227
- **fitness_score**: 0.561  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prep | 1.00 | 1.00 | 0.1191 |
| descend_to_peg_height | 1.00 | 1.00 | 0.1609 |
| align_contact | 1.00 | 1.00 | 0.0297 |
| push_channel | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prep | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.130, 0.207) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.535 | 4.034 |
| descend_to_peg_height | descend | 1.00 / step_budget | (0.509, 0.130, 0.207)→(0.499, 0.117, 0.048) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.543 | 0.595 |
| align_contact | align | 1.00 / step_budget | (0.499, 0.117, 0.048)→(0.500, 0.092, 0.032) | (0.502, 0.067, 0.034)→(0.503, 0.063, 0.035) | 0.147→0.143 | 1.00 / 2.333 | 1.514 | 11.820 |
| push_channel | push | 0.00 / guard_failure | (0.499, -0.054, 0.028)→(0.499, -0.054, 0.028) | (0.503, 0.063, 0.035)→(0.499, -0.082, 0.036) | 0.143→0.006 | 1.00 / 2.333 | 15.083 | 41.166 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.069
- terminal_score: 0.288
- phase_score: 0.802
- phase_breakdown.push_through_score: 0.976
- phase_breakdown.align_to_peg_score: 0.610
- phase_breakdown.reach_peg_score: 0.652

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.596
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.288
- **Median Q (composite search score)**: -0.013
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.251


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35088,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.align_speed":0.07389,"align_contact.align_x_offset":0.00099,"approach_prep.approach_height":0.1624,"approach_prep.approach_speed":0.19141,"descend_to_peg_height.descend_speed":0.09977,"push_channel.push_distance":0.19124,"push_channel.push_force_guard_threshold":37.15689,"push_channel.push_lateral_offset":0.00533,"push_channel.push_retry_x_offset":-0.00263,"push_channel.push_speed":0.03868},"optimized_scores":{"best_composite_score":-0.02004,"best_fitness_score":0.53996,"best_task_score":0.1948},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":174.0,"contact_point_centroid":[0.5029,0.00525,0.03905],"force_p95":25.95747,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.03599,"mean_force":3.38236,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50151,0.01675,0.02779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49427,-0.10058,0.02292],"force_p95":45.07509,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.17295,"mean_force":34.76816,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50365,-0.05474,0.02786]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":45.0,"contact_point_centroid":[0.52516,0.0366,0.03605],"force_p95":27.47505,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.49896,"mean_force":5.38334,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5009,0.06656,0.02909]},{"body_a":"peg","body_b":"channel_base_body","contact_count":120.0,"contact_point_centroid":[0.49993,-0.01873,0.00976],"force_p95":7.28072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.69065,"mean_force":2.54167,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50166,0.02085,0.0282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":150.0,"contact_point_centroid":[0.50571,0.06085,0.00942],"force_p95":1.99917,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.73808,"mean_force":0.86489,"phase_index":2.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.50241,0.10226,0.03945]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50541,0.07927,0.04767],"force_p95":11.15881,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.40994,"mean_force":3.87676,"phase_index":2.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.5025,0.09122,0.03335]},{"body_a":"peg","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52288,0.00742,0.06463],"force_p95":8.73504,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.76045,"mean_force":5.16846,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5009,0.03034,0.02752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":196.0,"contact_point_centroid":[0.50516,0.06304,0.00931],"force_p95":0.75627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.61555,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51176,0.16022,0.25169]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.5009,0.196,0.29499]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.50607,0.06303,0.00938],"force_p95":0.55202,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55664,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51286,0.12032,0.13129]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,-0.0772,0.05949],"force_p95":0.36943,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38013,"mean_force":0.27315,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50347,-0.04905,0.02786]}],"total_contact_groups":11},"final_pose_error":0.04653,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49362,-0.08392,0.03529],"final_tcp_position":[0.50371,-0.05575,0.02784],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":46.03599,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":224.0,"n_steps_budget":600.0,"object_pos_end":[0.50602,0.06302,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55172,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":230.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52246,0.1272,0.21375],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06297,0.03381],"object_pos_start":[0.50602,0.06302,0.0338],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14328,"object_z_max":0.03381,"peak_contact_force":0.54523,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":382.0,"raw_peak_contact_force":0.55664,"subtask_id":"align_to_peg","tcp_end":[0.5044,0.11378,0.04837],"tcp_start":[0.52246,0.1272,0.21375],"tcp_to_object_dist_end":0.05288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":158.0,"n_steps_budget":600.0,"object_pos_end":[0.50693,0.05973,0.03514],"object_pos_start":[0.50603,0.06297,0.03381],"object_to_goal_dist_end":0.13999,"object_to_goal_dist_start":0.14323,"object_z_max":0.03539,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":163.0,"raw_peak_contact_force":11.73808,"subtask_id":"align_to_peg","tcp_end":[0.50262,0.08938,0.03244],"tcp_start":[0.5044,0.11378,0.04837],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.49388,-0.08313,0.0352],"object_pos_start":[0.50693,0.05973,0.03514],"object_to_goal_dist_end":0.00838,"object_to_goal_dist_start":0.13999,"object_z_max":0.03916,"peak_contact_force":32.28786,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":350.0,"raw_peak_contact_force":46.03599,"subtask_id":"push_through","tcp_end":[0.50371,-0.05575,0.02784],"tcp_start":[0.50371,-0.05545,0.02786],"tcp_to_object_dist_end":0.03,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40361,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.align_speed":0.06955,"align_contact.align_x_offset":0.00458,"approach_prep.approach_height":0.13912,"approach_prep.approach_speed":0.16826,"descend_to_peg_height.descend_speed":0.09558,"push_channel.push_distance":0.21073,"push_channel.push_force_guard_threshold":27.24362,"push_channel.push_lateral_offset":-0.00251,"push_channel.push_retry_x_offset":-0.00405,"push_channel.push_speed":0.0375},"optimized_scores":{"best_composite_score":-0.01345,"best_fitness_score":0.54655,"best_task_score":0.19862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":141.0,"contact_point_centroid":[0.50212,-0.00036,0.03877],"force_p95":6.27201,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.91015,"mean_force":1.72377,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50186,0.01096,0.02759]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50195,-0.10004,0.05992],"force_p95":28.6865,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.95017,"mean_force":15.92572,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50112,-0.05194,0.02759]},{"body_a":"peg","body_b":"channel_base_body","contact_count":120.0,"contact_point_centroid":[0.50127,-0.01261,0.00956],"force_p95":7.60571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.5846,"mean_force":2.34429,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50221,0.02324,0.02794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":168.0,"contact_point_centroid":[0.50626,0.05514,0.00944],"force_p95":1.80567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.59615,"mean_force":0.81762,"phase_index":2.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.50448,0.09518,0.03894]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.50692,0.07274,0.04561],"force_p95":10.11236,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.20744,"mean_force":2.32388,"phase_index":2.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.50546,0.08463,0.03315]},{"body_a":"peg","body_b":"channel_base_body","contact_count":229.0,"contact_point_centroid":[0.50544,0.05675,0.00932],"force_p95":0.68702,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.61583,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51514,0.15654,0.24002]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.50122,0.19576,0.29393]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47495,-0.00279,0.05994],"force_p95":1.12521,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14853,"mean_force":0.93392,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50186,0.02596,0.02729]},{"body_a":"peg","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.51594,0.02026,0.06553],"force_p95":0.81026,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.00371,"mean_force":0.21202,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50208,0.04853,0.02723]},{"body_a":"peg","body_b":"channel_base_body","contact_count":332.0,"contact_point_centroid":[0.5062,0.05651,0.00937],"force_p95":0.63485,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64396,"mean_force":0.54638,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51672,0.11356,0.12036]}],"total_contact_groups":10},"final_pose_error":0.07551,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.502,-0.08212,0.03569],"final_tcp_position":[0.50104,-0.05278,0.0275],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":30.91015,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":258.0,"n_steps_budget":600.0,"object_pos_end":[0.50614,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.50098,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":266.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.52886,0.11994,0.19177],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05662,0.03382],"object_pos_start":[0.50614,0.0566,0.03377],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03382,"peak_contact_force":0.54387,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":332.0,"raw_peak_contact_force":0.64396,"subtask_id":"align_to_peg","tcp_end":[0.50554,0.1075,0.04835],"tcp_start":[0.52886,0.11994,0.19177],"tcp_to_object_dist_end":0.05292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":171.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.05297,0.03515],"object_pos_start":[0.50614,0.05662,0.03382],"object_to_goal_dist_end":0.13319,"object_to_goal_dist_start":0.1369,"object_z_max":0.03532,"peak_contact_force":0.41805,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":190.0,"raw_peak_contact_force":11.59615,"subtask_id":"align_to_peg","tcp_end":[0.50576,0.08262,0.03216],"tcp_start":[0.50554,0.1075,0.04835],"tcp_to_object_dist_end":0.0298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.50217,-0.08149,0.03536],"object_pos_start":[0.50593,0.05297,0.03515],"object_to_goal_dist_end":0.00533,"object_to_goal_dist_start":0.13319,"object_z_max":0.0398,"peak_contact_force":0.51351,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":282.0,"raw_peak_contact_force":30.91015,"subtask_id":"push_through","tcp_end":[0.50104,-0.05278,0.0275],"tcp_start":[0.50109,-0.05243,0.02756],"tcp_to_object_dist_end":0.02979,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28105,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.align_speed":0.05412,"align_contact.align_x_offset":0.00495,"approach_prep.approach_height":0.16202,"approach_prep.approach_speed":0.12715,"descend_to_peg_height.descend_speed":0.13063,"push_channel.push_distance":0.22434,"push_channel.push_force_guard_threshold":34.95311,"push_channel.push_lateral_offset":0.0041,"push_channel.push_retry_x_offset":-9e-05,"push_channel.push_speed":0.04799},"optimized_scores":{"best_composite_score":0.03617,"best_fitness_score":0.59617,"best_task_score":0.28807},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.4983,-0.10034,0.0615],"force_p95":44.50662,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.5529,"mean_force":29.41036,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49305,-0.05235,0.02751]},{"body_a":"attachment","body_b":"peg","contact_count":179.0,"contact_point_centroid":[0.49533,0.00671,0.04269],"force_p95":27.52998,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.09505,"mean_force":4.08928,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49182,0.01825,0.0276]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":42.0,"contact_point_centroid":[0.47475,-0.00974,0.04651],"force_p95":29.80547,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.13041,"mean_force":9.05475,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4918,0.02087,0.02755]},{"body_a":"peg","body_b":"channel_base_body","contact_count":121.0,"contact_point_centroid":[0.50003,0.0003,0.00934],"force_p95":8.6877,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.23239,"mean_force":2.67734,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49156,0.03824,0.0278]},{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.49381,0.07736,0.00945],"force_p95":4.98251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.12485,"mean_force":1.06032,"phase_index":2.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.48958,0.11787,0.03853]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.49406,0.09558,0.04438],"force_p95":10.6033,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.71301,"mean_force":3.73183,"phase_index":2.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.49226,0.10754,0.03303]},{"body_a":"peg","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.51014,0.00939,0.06524],"force_p95":2.30336,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.4951,"mean_force":0.96787,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49134,0.03452,0.02733]},{"body_a":"peg","body_b":"channel_base_body","contact_count":170.0,"contact_point_centroid":[0.49474,0.0798,0.00933],"force_p95":0.81034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.62156,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.48555,0.16855,0.25289]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.49807,0.19626,0.2944]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52503,-0.0667,0.05872],"force_p95":0.59976,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60632,"mean_force":0.5407,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49284,-0.03763,0.02759]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.49378,0.08002,0.00938],"force_p95":0.56661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5839,"mean_force":0.54656,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.48057,0.13653,0.1322]}],"total_contact_groups":11},"final_pose_error":0.06587,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50018,-0.0832,0.03709],"final_tcp_position":[0.49297,-0.05362,0.02739],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":46.5529,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":198.0,"n_steps_budget":630.0,"object_pos_end":[0.49384,0.07996,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55117,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":205.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.47436,0.14296,0.21646],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":405.0,"n_steps_budget":900.0,"object_pos_end":[0.49382,0.07994,0.03378],"object_pos_start":[0.49384,0.07996,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.1602,"object_z_max":0.03379,"peak_contact_force":0.53855,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":405.0,"raw_peak_contact_force":0.5839,"subtask_id":"align_to_peg","tcp_end":[0.48856,0.13042,0.0477],"tcp_start":[0.47436,0.14296,0.21646],"tcp_to_object_dist_end":0.05263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":188.0,"n_steps_budget":600.0,"object_pos_end":[0.49473,0.07529,0.03478],"object_pos_start":[0.49382,0.07994,0.03378],"object_to_goal_dist_end":0.15547,"object_to_goal_dist_start":0.16018,"object_z_max":0.03524,"peak_contact_force":4.12286,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":206.0,"raw_peak_contact_force":12.12485,"subtask_id":"align_to_peg","tcp_end":[0.49304,0.10513,0.03188],"tcp_start":[0.48856,0.13042,0.0477],"tcp_to_object_dist_end":0.03003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.50018,-0.08239,0.03719],"object_pos_start":[0.49473,0.07529,0.03478],"object_to_goal_dist_end":0.00369,"object_to_goal_dist_start":0.15547,"object_z_max":0.04032,"peak_contact_force":12.44808,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":386.0,"raw_peak_contact_force":46.5529,"subtask_id":"push_through","tcp_end":[0.49297,-0.05362,0.02739],"tcp_start":[0.49304,-0.05332,0.02746],"tcp_to_object_dist_end":0.03124,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```