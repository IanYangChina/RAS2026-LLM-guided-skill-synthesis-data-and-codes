## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.3200 | 0.56 | ✅ accepted |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0222 | 0.32 | ❌ rejected |
| 7 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.1539 | 0.12 | ❌ rejected |
| 6 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2651 | 0.36 | ✅ accepted |
| 5 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.3940 | 0.35 | ✅ accepted |

**Proposal policy**: task_score is 0.56 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.320) — your mutation base

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

- **Composite score**: 0.320
- **task_score** (E): 0.558
- **fitness_score**: 0.663  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prep | 1.00 | 1.00 | 0.1195 |
| descend_to_peg_height | 1.00 | 1.00 | 0.1603 |
| lateral_contact | 0.67 | 1.00 | 0.0306 |
| push_channel | 0.33 | 1.00 | 0.1717 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prep | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.130, 0.207) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.533 | 4.034 |
| descend_to_peg_height | descend | 1.00 / step_budget | (0.509, 0.130, 0.207)→(0.499, 0.117, 0.048) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.546 | 0.583 |
| lateral_contact | contact | 0.67 / force_exceeded | (0.499, 0.117, 0.048)→(0.497, 0.092, 0.032) | (0.502, 0.067, 0.034)→(0.502, 0.063, 0.035) | 0.147→0.143 | 1.00 / 2.333 | 4.034 | 5.762 |
| push_channel | push | 0.33 / step_budget | (0.497, 0.092, 0.032)→(0.498, -0.079, 0.030) | (0.502, 0.063, 0.035)→(0.504, -0.090, 0.038) | 0.143→0.020 | 1.00 / 5.000 | 231.088 | 373.080 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.717
- phase_score: 0.743
- phase_breakdown.push_through_score: 0.856
- phase_breakdown.align_to_peg_score: 0.631
- phase_breakdown.reach_peg_score: 0.627

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.733
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.717
- **Median Q (composite search score)**: 0.404
- **K-run variance**: 0.0288
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.290


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1086,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.14986,"approach_prep.approach_speed":0.08864,"descend_to_peg_height.descend_speed":0.05845,"lateral_contact.contact_force_threshold":5.01859,"lateral_contact.contact_speed":0.06748,"lateral_contact.contact_x_offset":-0.01136,"push_channel.push_distance":0.25449,"push_channel.push_lateral_offset":-0.00787,"push_channel.push_speed":0.04383},"optimized_scores":{"best_composite_score":0.40413,"best_fitness_score":0.66413,"best_task_score":0.57493},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":616.0,"contact_point_centroid":[0.53579,-0.1,0.06495],"force_p95":248.41224,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":388.0019,"mean_force":181.4314,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48771,-0.06979,0.02907]},{"body_a":"attachment","body_b":"peg","contact_count":931.0,"contact_point_centroid":[0.49919,-0.05521,0.05474],"force_p95":213.26493,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":234.42935,"mean_force":120.13198,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48778,-0.04777,0.02908]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":952.0,"contact_point_centroid":[0.52665,-0.06561,0.05072],"force_p95":164.74813,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":184.42894,"mean_force":80.85259,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48774,-0.04728,0.02905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":705.0,"contact_point_centroid":[0.51122,-0.10215,0.05803],"force_p95":129.8298,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.53164,"mean_force":99.44454,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48766,-0.06924,0.02904]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":298.0,"contact_point_centroid":[0.47499,-0.06146,0.03064],"force_p95":103.90996,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.64248,"mean_force":65.50646,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48681,-0.06143,0.02863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":889.0,"contact_point_centroid":[0.51589,-0.08156,0.00965],"force_p95":45.6466,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.76697,"mean_force":22.62154,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48772,-0.05117,0.02906]},{"body_a":"peg","body_b":"link7","contact_count":135.0,"contact_point_centroid":[0.51941,-0.00628,0.06441],"force_p95":47.43855,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.24221,"mean_force":26.15531,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48733,0.0072,0.02878]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50111,0.07915,0.05987],"force_p95":5.67138,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.34806,"mean_force":2.98656,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.4934,0.09071,0.03321]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.50646,0.06089,0.00941],"force_p95":0.56087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.11489,"mean_force":0.65499,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.49714,0.10068,0.03856]},{"body_a":"peg","body_b":"channel_base_body","contact_count":224.0,"contact_point_centroid":[0.50532,0.06285,0.00932],"force_p95":0.68709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.60694,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51157,0.16027,0.24608]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.50069,0.19659,0.29523]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52503,0.06081,0.06],"force_p95":2.41629,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41629,"mean_force":2.41629,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.49291,0.08923,0.03249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50607,0.063,0.00938],"force_p95":0.55207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55641,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51281,0.11989,0.12584]}],"total_contact_groups":13},"final_pose_error":0.089,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51468,-0.08823,0.03321],"final_tcp_position":[0.49082,-0.07657,0.02988],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":388.0019,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06302,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54428,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":258.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.5225,0.12633,0.20225],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.50595,0.06302,0.03381],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14328,"object_z_max":0.03381,"peak_contact_force":0.54319,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":378.0,"raw_peak_contact_force":0.55641,"subtask_id":"align_to_peg","tcp_end":[0.50441,0.11379,0.04864],"tcp_start":[0.5225,0.12633,0.20225],"tcp_to_object_dist_end":0.05297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":250.0,"n_steps_budget":600.0,"object_pos_end":[0.50656,0.06186,0.03544],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.14209,"object_to_goal_dist_start":0.14322,"object_z_max":0.03543,"peak_contact_force":7.34806,"phase_name":"lateral_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":262.0,"raw_peak_contact_force":7.34806,"subtask_id":"align_to_peg","tcp_end":[0.49288,0.08915,0.03245],"tcp_start":[0.50441,0.11379,0.04864],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51468,-0.08823,0.03321],"object_pos_start":[0.50656,0.06186,0.03544],"object_to_goal_dist_end":0.01815,"object_to_goal_dist_start":0.14209,"object_z_max":0.03789,"peak_contact_force":226.32155,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4526.0,"raw_peak_contact_force":388.0019,"subtask_id":"push_through","tcp_end":[0.49082,-0.07657,0.02988],"tcp_start":[0.49288,0.08915,0.03245],"tcp_to_object_dist_end":0.02677,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09091,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.14765,"approach_prep.approach_speed":0.12415,"descend_to_peg_height.descend_speed":0.06324,"lateral_contact.contact_force_threshold":5.3633,"lateral_contact.contact_speed":0.0227,"lateral_contact.contact_x_offset":0.0049,"push_channel.push_distance":0.22628,"push_channel.push_lateral_offset":-0.01953,"push_channel.push_speed":0.03033},"optimized_scores":{"best_composite_score":0.08306,"best_fitness_score":0.59306,"best_task_score":0.38247},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":743.0,"contact_point_centroid":[0.54051,-0.1,0.06495],"force_p95":255.59607,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":339.95514,"mean_force":175.9773,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49391,-0.07125,0.02875]},{"body_a":"peg","body_b":"channel_base_body","contact_count":771.0,"contact_point_centroid":[0.5101,-0.10426,0.05212],"force_p95":221.05128,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":249.86301,"mean_force":154.29973,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4939,-0.071,0.02871]},{"body_a":"attachment","body_b":"peg","contact_count":952.0,"contact_point_centroid":[0.50253,-0.06261,0.05417],"force_p95":240.74133,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":249.18395,"mean_force":156.73034,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49486,-0.05419,0.02823]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":645.0,"contact_point_centroid":[0.5277,-0.0903,0.05332],"force_p95":158.98004,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.01097,"mean_force":117.63454,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49393,-0.07217,0.02895]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53251,-0.00312,0.06],"force_p95":90.92383,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.26494,"mean_force":85.17385,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49616,-0.00956,0.02543]},{"body_a":"peg","body_b":"channel_base_body","contact_count":692.0,"contact_point_centroid":[0.51787,-0.08733,0.0094],"force_p95":48.33649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.33898,"mean_force":28.68276,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49481,-0.05758,0.02862]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.4746,-0.07267,0.04106],"force_p95":57.87689,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.14477,"mean_force":25.7648,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4939,-0.04401,0.0259]},{"body_a":"peg","body_b":"channel_base_body","contact_count":763.0,"contact_point_centroid":[0.5061,0.05213,0.00952],"force_p95":2.00104,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.64603,"mean_force":0.73479,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50449,0.09077,0.03619]},{"body_a":"attachment","body_b":"peg","contact_count":187.0,"contact_point_centroid":[0.50659,0.07031,0.03827],"force_p95":2.5399,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.18156,"mean_force":0.98912,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50586,0.08232,0.03192]},{"body_a":"peg","body_b":"channel_base_body","contact_count":233.0,"contact_point_centroid":[0.50561,0.05649,0.00932],"force_p95":0.68236,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.61465,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51491,0.15685,0.24431]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.5011,0.19591,0.29449]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50612,0.05668,0.00938],"force_p95":0.59798,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60776,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51647,0.11375,0.12442]}],"total_contact_groups":12},"final_pose_error":0.07579,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.514,-0.09,0.03329],"final_tcp_position":[0.49486,-0.07306,0.02951],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":339.95514,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":262.0,"n_steps_budget":780.0,"object_pos_end":[0.50612,0.05664,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.50487,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":270.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.52867,0.1203,0.19945],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.0566,0.03378],"object_pos_start":[0.50612,0.05664,0.03377],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13691,"object_z_max":0.03379,"peak_contact_force":0.54993,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":363.0,"raw_peak_contact_force":0.60776,"subtask_id":"align_to_peg","tcp_end":[0.50526,0.10749,0.04846],"tcp_start":[0.52867,0.1203,0.19945],"tcp_to_object_dist_end":0.05297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":763.0,"n_steps_budget":960.0,"object_pos_end":[0.50582,0.04792,0.03423],"object_pos_start":[0.50612,0.0566,0.03378],"object_to_goal_dist_end":0.12818,"object_to_goal_dist_start":0.13688,"object_z_max":0.03492,"peak_contact_force":0.46189,"phase_name":"lateral_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":950.0,"raw_peak_contact_force":5.64603,"subtask_id":"align_to_peg","tcp_end":[0.50666,0.07783,0.02977],"tcp_start":[0.50526,0.10749,0.04846],"tcp_to_object_dist_end":0.03026,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.514,-0.09,0.03329],"object_pos_start":[0.50582,0.04792,0.03423],"object_to_goal_dist_end":0.01847,"object_to_goal_dist_start":0.12818,"object_z_max":0.0394,"peak_contact_force":253.95688,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3840.0,"raw_peak_contact_force":339.95514,"subtask_id":"push_through","tcp_end":[0.49486,-0.07306,0.02951],"tcp_start":[0.50666,0.07783,0.02977],"tcp_to_object_dist_end":0.02585,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04545,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.16482,"approach_prep.approach_speed":0.16773,"descend_to_peg_height.descend_speed":0.04356,"lateral_contact.contact_force_threshold":4.22413,"lateral_contact.contact_speed":0.03138,"lateral_contact.contact_x_offset":0.00325,"push_channel.push_distance":0.23069,"push_channel.push_lateral_offset":0.01503,"push_channel.push_speed":0.04948},"optimized_scores":{"best_composite_score":0.47267,"best_fitness_score":0.73267,"best_task_score":0.71744},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.51362,-0.10031,0.065],"force_p95":337.85086,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.28151,"mean_force":212.84302,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50835,-0.0881,0.03186]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52501,-0.08791,0.06],"force_p95":290.38683,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.24084,"mean_force":173.90856,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50841,-0.0874,0.03187]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50292,-0.10481,0.05372],"force_p95":191.26321,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":231.35597,"mean_force":127.62876,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50281,-0.06858,0.02903]},{"body_a":"attachment","body_b":"peg","contact_count":665.0,"contact_point_centroid":[0.50308,-0.04318,0.0512],"force_p95":166.74664,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":205.19343,"mean_force":95.1716,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49889,-0.03345,0.02919]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":84.0,"contact_point_centroid":[0.47133,-0.10235,0.0375],"force_p95":195.34244,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":203.42232,"mean_force":77.97616,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50822,-0.08631,0.0317]},{"body_a":"channel_base_body","body_b":"link7","contact_count":221.0,"contact_point_centroid":[0.55123,-0.1,0.06499],"force_p95":153.26326,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.90196,"mean_force":92.83628,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50077,-0.06357,0.02822]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":477.0,"contact_point_centroid":[0.52557,-0.06253,0.05189],"force_p95":57.63082,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.45112,"mean_force":22.4302,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49756,-0.03699,0.02839]},{"body_a":"peg","body_b":"channel_base_body","contact_count":98.0,"contact_point_centroid":[0.50253,-0.01234,0.00981],"force_p95":36.87776,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.69035,"mean_force":14.47285,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49351,0.02922,0.02996]},{"body_a":"peg","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.49381,0.07935,0.00938],"force_p95":0.55404,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.29261,"mean_force":0.58338,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.4882,0.11848,0.03837]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49365,0.09774,0.05515],"force_p95":3.8988,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.98839,"mean_force":2.5088,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.4902,0.10976,0.03395]},{"body_a":"peg","body_b":"channel_base_body","contact_count":167.0,"contact_point_centroid":[0.49476,0.08002,0.00933],"force_p95":0.82434,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.62294,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.48557,0.16849,0.25404]},{"body_a":"peg","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52197,0.02359,0.0653],"force_p95":2.80074,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.29499,"mean_force":0.82375,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49182,0.04029,0.0296]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.49802,0.19613,0.29435]},{"body_a":"peg","body_b":"channel_base_body","contact_count":452.0,"contact_point_centroid":[0.49378,0.07993,0.00938],"force_p95":0.56433,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5858,"mean_force":0.5466,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.48039,0.13655,0.13363]}],"total_contact_groups":14},"final_pose_error":0.03384,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.48193,-0.09295,0.04604],"final_tcp_position":[0.50836,-0.08757,0.03183],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":391.28151,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":195.0,"n_steps_budget":600.0,"object_pos_end":[0.49379,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54936,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":202.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.47441,0.14305,0.21883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07996,0.03378],"object_pos_start":[0.49379,0.07993,0.03378],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16017,"object_z_max":0.03379,"peak_contact_force":0.5458,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":452.0,"raw_peak_contact_force":0.5858,"subtask_id":"align_to_peg","tcp_end":[0.4885,0.13038,0.04762],"tcp_start":[0.47441,0.14305,0.21883],"tcp_to_object_dist_end":0.05255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":369.0,"n_steps_budget":690.0,"object_pos_end":[0.49382,0.07973,0.03429],"object_pos_start":[0.49383,0.07996,0.03378],"object_to_goal_dist_end":0.15995,"object_to_goal_dist_start":0.1602,"object_z_max":0.03425,"peak_contact_force":4.29261,"phase_name":"lateral_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":375.0,"raw_peak_contact_force":4.29261,"subtask_id":"align_to_peg","tcp_end":[0.49029,0.10948,0.03382],"tcp_start":[0.4885,0.13038,0.04762],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.48193,-0.09295,0.04604],"object_pos_start":[0.49382,0.07973,0.03429],"object_to_goal_dist_end":0.02304,"object_to_goal_dist_start":0.15995,"object_z_max":0.04602,"peak_contact_force":212.98521,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2065.0,"raw_peak_contact_force":391.28151,"subtask_id":"push_through","tcp_end":[0.50836,-0.08757,0.03183],"tcp_start":[0.49029,0.10948,0.03382],"tcp_to_object_dist_end":0.03049,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```