## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | pose_tolerance | 10 | 0.1653 | 0.26 | ❌ rejected |
| 13 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | pose_tolerance | 9 | 0.2843 | 0.28 | ✅ accepted |
| 12 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.0437 | 0.12 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3691 | 0.18 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.0845 | 0.12 | ❌ rejected |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.165) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.05
  weight: 0.3
- id: push_through_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.06
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    lateral_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: contact_peg
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
    contact_force:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: peg_contact
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
  subtask_id: reach_peg
- id: align_pusher
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - -1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_through_channel
- id: push_along_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_time_limit:
      type: scalar
      range:
      - 2.0
      - 6.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: push_through_channel
- id: retract_from_channel
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=peg_contact, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]
- **align_pusher** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, -1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time_limit: status=consumed; consumers=duration.max_time (replace)
- **retract_from_channel** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.165
- **task_score** (E): 0.262
- **fitness_score**: 0.505  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2123 |
| contact_peg | 1.00 | 1.00 | 0.0566 |
| align_behind_peg | 1.00 | 1.00 | 0.0301 |
| push_along_channel | 0.67 | 1.00 | 0.1062 |
| retract_from_channel | 1.00 | 1.00 | 0.0819 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.511, 0.130, 0.101) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.546 | 4.034 |
| contact_peg | contact | 1.00 / force_exceeded | (0.511, 0.130, 0.101)→(0.502, 0.094, 0.059) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 16.620 | 16.620 |
| align_behind_peg | align | 1.00 / step_budget | (0.502, 0.094, 0.059)→(0.499, 0.079, 0.034) | (0.502, 0.067, 0.034)→(0.501, 0.040, 0.031) | 0.147→0.121 | 1.00 / 1.333 | 1.186 | 166.357 |
| push_along_channel | push | 0.67 / time_limit | (0.499, 0.079, 0.034)→(0.495, -0.027, 0.031) | (0.501, 0.040, 0.031)→(0.506, -0.057, 0.033) | 0.121→0.027 | 1.00 / 2.000 | 14.284 | 29.845 |
| retract_from_channel | retract | 1.00 / step_budget | (0.493, -0.013, 0.031)→(0.490, -0.013, 0.113) | (0.505, -0.045, 0.032)→(0.503, -0.046, 0.029) | 0.037→0.037 | 1.00 / 1.000 | 0.567 | 121.698 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.869
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.253
- phase_score: 0.771
- phase_breakdown.push_through_channel_score: 0.929
- phase_breakdown.reach_peg_score: 0.401

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.564
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.294
- **Median Q (composite search score)**: 0.177
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.311


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45714,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_peg.align_speed":0.03896,"approach_peg.approach_height":0.05056,"approach_peg.lateral_offset":0.00216,"approach_peg.speed":0.09917,"contact_peg.contact_force":4.20628,"push_along_channel.push_distance":0.1985,"push_along_channel.push_speed":0.04965,"push_along_channel.push_time_limit":4.79787,"retract_from_channel.retract_height":0.07221,"retract_from_channel.speed":0.06536},"optimized_scores":{"best_composite_score":0.17701,"best_fitness_score":0.51701,"best_task_score":0.29387},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.50135,0.04734,0.00961],"force_p95":53.18259,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.31972,"mean_force":9.4483,"phase_index":2.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.50748,0.08521,0.04705]},{"body_a":"attachment","body_b":"peg","contact_count":97.0,"contact_point_centroid":[0.50642,0.07303,0.04641],"force_p95":62.10222,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.85286,"mean_force":14.21909,"phase_index":2.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.50717,0.08472,0.04618]},{"body_a":"peg","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.50604,0.06293,0.00938],"force_p95":0.55144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.5057,"mean_force":0.60591,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51805,0.10952,0.07687]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51123,0.08018,0.05877],"force_p95":16.10091,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.10091,"mean_force":16.10091,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51174,0.09215,0.05873]},{"body_a":"attachment","body_b":"peg","contact_count":831.0,"contact_point_centroid":[0.50312,0.01467,0.04148],"force_p95":5.97731,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.92441,"mean_force":2.67727,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49935,0.02638,0.03135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":729.0,"contact_point_centroid":[0.50484,-0.01462,0.00992],"force_p95":6.28003,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.11154,"mean_force":3.34645,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49947,0.02997,0.0314]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":339.0,"contact_point_centroid":[0.52504,-0.0223,0.02331],"force_p95":2.41722,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.75894,"mean_force":0.8532,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49899,0.00633,0.03147]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.50574,0.06297,0.00936],"force_p95":0.56032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56722,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51278,0.16191,0.1941]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5,0.19846,0.2961]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":149.0,"contact_point_centroid":[0.52501,-0.05087,0.05059],"force_p95":0.66859,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92848,"mean_force":0.12539,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49562,-0.02224,0.0609]},{"body_a":"attachment","body_b":"peg","contact_count":65.0,"contact_point_centroid":[0.50269,-0.03392,0.05974],"force_p95":1.34861,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.83272,"mean_force":0.36325,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49607,-0.0223,0.03856]},{"body_a":"peg","body_b":"channel_base_body","contact_count":575.0,"contact_point_centroid":[0.50669,-0.05419,0.00952],"force_p95":0.56192,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73802,"mean_force":0.51803,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49527,-0.02221,0.06323]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50694,-0.05084,0.03379],"final_tcp_position":[0.49516,-0.02218,0.09474],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":69.31972,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06304,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54333,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":689.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.5264,0.12674,0.09784],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":269.0,"n_steps_budget":600.0,"object_pos_end":[0.50594,0.06301,0.0338],"object_pos_start":[0.50598,0.06304,0.0338],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.1433,"object_z_max":0.03381,"peak_contact_force":16.5057,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":270.0,"raw_peak_contact_force":16.5057,"subtask_id":"reach_peg","tcp_end":[0.51171,0.09203,0.05861],"tcp_start":[0.5264,0.12674,0.09784],"tcp_to_object_dist_end":0.03861,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":171.0,"n_steps_budget":600.0,"object_pos_end":[0.50124,0.047,0.03424],"object_pos_start":[0.50594,0.06301,0.0338],"object_to_goal_dist_end":0.12714,"object_to_goal_dist_start":0.14327,"object_z_max":0.03814,"peak_contact_force":0.75481,"phase_name":"align_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":250.0,"raw_peak_contact_force":69.31972,"subtask_id":"push_through_channel","tcp_end":[0.50361,0.07716,0.03507],"tcp_start":[0.51171,0.09203,0.05861],"tcp_to_object_dist_end":0.03026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,-0.05131,0.03565],"object_pos_start":[0.50124,0.047,0.03424],"object_to_goal_dist_end":0.02986,"object_to_goal_dist_start":0.12714,"object_z_max":0.03581,"peak_contact_force":0.58436,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1899.0,"raw_peak_contact_force":9.92441,"subtask_id":"push_through_channel","tcp_end":[0.49867,-0.02225,0.03185],"tcp_start":[0.50361,0.07716,0.03507],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":575.0,"n_steps_budget":720.0,"object_pos_end":[0.50694,-0.05084,0.03379],"object_pos_start":[0.507,-0.05131,0.03565],"object_to_goal_dist_end":0.03061,"object_to_goal_dist_start":0.02986,"object_z_max":0.03565,"peak_contact_force":0.54571,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":789.0,"raw_peak_contact_force":1.92848,"tcp_end":[0.49516,-0.02218,0.09474],"tcp_start":[0.49867,-0.02225,0.03185],"tcp_to_object_dist_end":0.06838,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57343,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_peg.align_speed":0.02125,"approach_peg.approach_height":0.05305,"approach_peg.lateral_offset":-0.00633,"approach_peg.speed":0.07219,"contact_peg.contact_force":6.32925,"push_along_channel.push_distance":0.15147,"push_along_channel.push_speed":0.07959,"push_along_channel.push_time_limit":5.11466,"retract_from_channel.retract_height":0.06771,"retract_from_channel.speed":0.06531},"optimized_scores":{"best_composite_score":0.22375,"best_fitness_score":0.56375,"best_task_score":0.2531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":102.0,"contact_point_centroid":[0.50641,0.06644,0.04659],"force_p95":57.43079,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.37645,"mean_force":14.70671,"phase_index":2.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.50664,0.07815,0.04643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":169.0,"contact_point_centroid":[0.50221,0.04034,0.00971],"force_p95":54.90659,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.33876,"mean_force":9.3089,"phase_index":2.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.5069,0.07857,0.04723]},{"body_a":"attachment","body_b":"peg","contact_count":767.0,"contact_point_centroid":[0.5018,-0.00482,0.03854],"force_p95":8.26901,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.11598,"mean_force":2.50722,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49902,0.00693,0.03166]},{"body_a":"peg","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.5067,-0.1004,0.05982],"force_p95":35.07171,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.93753,"mean_force":18.83431,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49814,-0.0534,0.0324]},{"body_a":"peg","body_b":"channel_base_body","contact_count":282.0,"contact_point_centroid":[0.50613,0.05661,0.00938],"force_p95":0.55018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.13685,"mean_force":0.61267,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51683,0.10304,0.07814]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51269,0.07336,0.05875],"force_p95":18.66736,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.66736,"mean_force":18.66736,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51088,0.08521,0.05905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":683.0,"contact_point_centroid":[0.50268,-0.02816,0.00991],"force_p95":7.06288,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.68291,"mean_force":2.5056,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49918,0.01388,0.03163]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":312.0,"contact_point_centroid":[0.52509,-0.04776,0.02673],"force_p95":3.77438,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.95915,"mean_force":0.96801,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49856,-0.01919,0.03192]},{"body_a":"peg","body_b":"channel_base_body","contact_count":676.0,"contact_point_centroid":[0.50594,0.05663,0.00936],"force_p95":0.60022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57012,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51192,0.15885,0.19526]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49994,0.19834,0.29598]}],"total_contact_groups":10},"final_pose_error":0.17742,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50682,-0.08236,0.03538],"final_tcp_position":[0.49808,-0.05423,0.03233],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":87.37645,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54519,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":713.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.52491,0.12083,0.10022],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":282.0,"n_steps_budget":600.0,"object_pos_end":[0.50614,0.05659,0.03378],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":19.13685,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":283.0,"raw_peak_contact_force":19.13685,"subtask_id":"reach_peg","tcp_end":[0.51085,0.08511,0.05894],"tcp_start":[0.52491,0.12083,0.10022],"tcp_to_object_dist_end":0.03832,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":188.0,"n_steps_budget":930.0,"object_pos_end":[0.50222,0.0409,0.0343],"object_pos_start":[0.50614,0.05659,0.03378],"object_to_goal_dist_end":0.12106,"object_to_goal_dist_start":0.13686,"object_z_max":0.03865,"peak_contact_force":2.26681,"phase_name":"align_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":271.0,"raw_peak_contact_force":87.37645,"subtask_id":"push_through_channel","tcp_end":[0.50351,0.07059,0.03505],"tcp_start":[0.51085,0.08511,0.05894],"tcp_to_object_dist_end":0.02973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,-0.08236,0.03538],"object_pos_start":[0.50222,0.0409,0.0343],"object_to_goal_dist_end":0.00857,"object_to_goal_dist_start":0.12106,"object_z_max":0.03599,"peak_contact_force":42.11598,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1785.0,"raw_peak_contact_force":42.11598,"subtask_id":"push_through_channel","tcp_end":[0.49808,-0.05423,0.03233],"tcp_start":[0.50351,0.07059,0.03505],"tcp_to_object_dist_end":0.02962,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19337,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_peg.align_speed":0.04337,"approach_peg.approach_height":0.05669,"approach_peg.lateral_offset":0.01189,"approach_peg.speed":0.05295,"contact_peg.contact_force":9.44431,"push_along_channel.push_distance":0.1649,"push_along_channel.push_speed":0.04075,"push_along_channel.push_time_limit":4.61875,"retract_from_channel.retract_height":0.11057,"retract_from_channel.speed":0.08092},"optimized_scores":{"best_composite_score":0.09529,"best_fitness_score":0.43529,"best_task_score":0.23944},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":42.0,"contact_point_centroid":[0.47498,0.09948,0.05989],"force_p95":324.50585,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.37474,"mean_force":241.9445,"phase_index":2.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.48576,0.10389,0.05823]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":150.0,"contact_point_centroid":[0.47499,-0.00347,0.04685],"force_p95":203.2013,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.46786,"mean_force":110.11495,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.4868,-0.00347,0.0448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.49846,0.06165,0.00879],"force_p95":107.8285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":124.83125,"mean_force":31.83297,"phase_index":2.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.48779,0.09871,0.04749]},{"body_a":"attachment","body_b":"peg","contact_count":143.0,"contact_point_centroid":[0.49624,0.09536,0.05663],"force_p95":108.77592,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.22547,"mean_force":68.58498,"phase_index":2.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.48734,0.10297,0.05667]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":215.0,"contact_point_centroid":[0.475,0.06983,0.03061],"force_p95":31.07409,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.49556,"mean_force":19.80802,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48683,0.06982,0.02866]},{"body_a":"peg","body_b":"channel_base_body","contact_count":349.0,"contact_point_centroid":[0.49378,0.08002,0.00938],"force_p95":0.55624,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.21743,"mean_force":0.5858,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48107,0.1245,0.08144]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49301,0.09791,0.05875],"force_p95":13.75805,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.75805,"mean_force":13.75805,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48441,0.10617,0.06001]},{"body_a":"attachment","body_b":"peg","contact_count":712.0,"contact_point_centroid":[0.49232,0.01892,0.04269],"force_p95":9.04214,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.64769,"mean_force":3.08799,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48728,0.03047,0.02895]},{"body_a":"peg","body_b":"channel_base_body","contact_count":841.0,"contact_point_centroid":[0.50493,-0.00391,0.00927],"force_p95":6.00785,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.06518,"mean_force":2.12848,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48716,0.04746,0.02893]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47483,0.05299,0.02523],"force_p95":6.51642,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.95613,"mean_force":2.29186,"phase_index":2.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.48756,0.09524,0.03966]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":387.0,"contact_point_centroid":[0.52502,-0.02132,0.02775],"force_p95":5.56297,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.21679,"mean_force":3.359,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48722,0.03377,0.02891]},{"body_a":"peg","body_b":"channel_base_body","contact_count":759.0,"contact_point_centroid":[0.5017,-0.04141,0.00829],"force_p95":0.69719,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.95343,"mean_force":0.63698,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48546,-0.00348,0.08037]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.525,-0.06004,0.02449],"force_p95":5.72914,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.8088,"mean_force":3.39155,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48589,-0.00346,0.06344]},{"body_a":"peg","body_b":"channel_base_body","contact_count":635.0,"contact_point_centroid":[0.49406,0.07992,0.00937],"force_p95":0.58473,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56668,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.489,0.17039,0.19853]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49921,0.19871,0.29634]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52511,0.02799,0.04766],"force_p95":1.63301,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69302,"mean_force":1.15023,"phase_index":2.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.48752,0.0981,0.04511]}],"total_contact_groups":17},"final_pose_error":0.01024,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49821,-0.0406,0.02414],"final_tcp_position":[0.48502,-0.00347,0.13049],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":342.37474,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07996,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54966,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":670.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.48022,0.14305,0.10573],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":349.0,"n_steps_budget":630.0,"object_pos_end":[0.49381,0.07992,0.03378],"object_pos_start":[0.49383,0.07996,0.03378],"object_to_goal_dist_end":0.16016,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":14.21743,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":350.0,"raw_peak_contact_force":14.21743,"subtask_id":"reach_peg","tcp_end":[0.48443,0.10608,0.05991],"tcp_start":[0.48022,0.14305,0.10573],"tcp_to_object_dist_end":0.03814,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":328.0,"n_steps_budget":600.0,"object_pos_end":[0.50024,0.03299,0.02414],"object_pos_start":[0.49381,0.07992,0.03378],"object_to_goal_dist_end":0.1141,"object_to_goal_dist_start":0.16016,"object_z_max":0.04084,"peak_contact_force":0.53631,"phase_name":"align_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":516.0,"raw_peak_contact_force":342.37474,"subtask_id":"push_through_channel","tcp_end":[0.4891,0.09069,0.0318],"tcp_start":[0.48443,0.10608,0.05991],"tcp_to_object_dist_end":0.05926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5028,-0.03815,0.02871],"object_pos_start":[0.50024,0.03299,0.02414],"object_to_goal_dist_end":0.04344,"object_to_goal_dist_start":0.1141,"object_z_max":0.02896,"peak_contact_force":0.15124,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2155.0,"raw_peak_contact_force":37.49556,"subtask_id":"push_through_channel","tcp_end":[0.48822,-0.00343,0.02964],"tcp_start":[0.4891,0.09069,0.0318],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":761.0,"n_steps_budget":870.0,"object_pos_end":[0.49821,-0.0406,0.02414],"object_pos_start":[0.5028,-0.03815,0.02871],"object_to_goal_dist_end":0.04251,"object_to_goal_dist_start":0.04344,"object_z_max":0.02871,"peak_contact_force":0.58803,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":971.0,"raw_peak_contact_force":241.46786,"tcp_end":[0.48502,-0.00347,0.13049],"tcp_start":[0.48822,-0.00343,0.02964],"tcp_to_object_dist_end":0.11342,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```