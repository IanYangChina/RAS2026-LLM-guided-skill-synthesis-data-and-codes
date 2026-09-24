## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.3039 | 0.02 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1315 | 0.22 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 7 | -0.3549 | 0.01 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2744 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.1268 | 0.10 | ❌ rejected |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.304) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.01
  weight: 0.3
- id: push_to_exit
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_overhead
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - 0.15
    tolerance: 0.03
  parameters:
    overhead_speed:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    overhead_tolerance:
      type: scalar
      range:
      - 0.015
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_peg
- id: align_behind_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.005
    tolerance: 0.01
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.03
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    align_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.008
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_peg
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.04
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    wall_force_threshold:
      type: scalar
      range:
      - 10.0
      - 50.0
      default: 30.0
      binds_to:
      - path: guards.wall_contact.threshold
        mode: replace
  guards:
  - id: wall_contact
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
  subtask_id: push_to_exit

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_overhead** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.15], tolerance=0.03
  - parameter_bindings:
    - overhead_speed: status=consumed; consumers=generator.speed (replace)
    - overhead_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=repeat
- **align_behind_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.005], tolerance=0.01
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=repeat
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - wall_force_threshold: status=consumed; consumers=guards.wall_contact.threshold (replace)
  - guards:
    - id=wall_contact, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]

## Design Metrics

- **Composite score**: -0.304
- **task_score** (E): 0.020
- **fitness_score**: 0.126  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_overhead | 1.00 | 1.00 | 0.0976 |
| align_behind_peg | 1.00 | 0.67 | 0.1868 |
| push_through_channel | 0.00 | 1.00 | 0.0005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_overhead | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.160, 0.214) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.667 | 0.097 | 16.243 |
| align_behind_peg | descend | 1.00 / step_budget | (0.508, 0.160, 0.214)→(0.499, 0.091, 0.042) | (0.502, 0.067, 0.034)→(0.504, 0.062, 0.037) | 0.147→0.142 | 0.67 / 0.667 | 0.396 | 33.213 |
| push_through_channel | push | 0.00 / guard_failure | (0.497, 0.086, 0.040)→(0.497, 0.085, 0.040) | (0.504, 0.062, 0.037)→(0.504, 0.057, 0.036) | 0.142→0.138 | 1.00 / 1.000 | 0.544 | 4.034 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.071
- alignment_error: None
- force_efficiency: 0.699
- terminal_score: 0.019
- phase_score: 0.221
- phase_breakdown.push_to_exit_score: 0.032
- phase_breakdown.reach_peg_score: 0.663

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.140
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.025
- **Median Q (composite search score)**: -0.304
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15447,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_peg.align_speed":0.04424,"align_behind_peg.align_tolerance":0.0165,"approach_overhead.overhead_speed":0.22247,"approach_overhead.overhead_tolerance":0.02587,"push_through_channel.contact_force_threshold":7.66357,"push_through_channel.push_distance":0.22563,"push_through_channel.push_speed":0.1172,"push_through_channel.push_tolerance":0.03189},"optimized_scores":{"best_composite_score":-0.30394,"best_fitness_score":0.12606,"best_task_score":0.02508},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50456,0.03903,0.00995],"force_p95":42.03112,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.03112,"mean_force":42.03112,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50204,0.08478,0.04063]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50428,0.07482,0.04103],"force_p95":26.81599,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.20305,"mean_force":6.11344,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50253,0.08666,0.04114]},{"body_a":"peg","body_b":"channel_base_body","contact_count":607.0,"contact_point_centroid":[0.5059,0.0616,0.0094],"force_p95":0.5544,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.69347,"mean_force":0.87658,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"descend","tcp_position_centroid":[0.51069,0.12252,0.12635]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.50478,0.07815,0.04751],"force_p95":18.58315,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.6034,"mean_force":12.95178,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"descend","tcp_position_centroid":[0.5036,0.09004,0.04724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.50473,0.06322,0.00925],"force_p95":1.1712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.66723,"phase_index":0.0,"phase_name":"approach_overhead","phase_type":"approach","tcp_position_centroid":[0.51144,0.17558,0.24988]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_overhead","phase_type":"approach","tcp_position_centroid":[0.50154,0.19646,0.29253]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52508,0.0587,0.01206],"force_p95":1.11686,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.12513,"mean_force":0.84956,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50242,0.08682,0.04101]}],"total_contact_groups":7},"final_pose_error":0.22069,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50641,0.05297,0.03612],"final_tcp_position":[0.50193,0.08303,0.04037],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":42.03112,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":140.0,"n_steps_budget":600.0,"object_pos_end":[0.50602,0.06299,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.17716,"phase_name":"approach_overhead","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":623.0,"raw_peak_contact_force":18.69347,"subtask_id":"reach_peg","tcp_end":[0.52032,0.15745,0.21404],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.5065,0.0587,0.03685],"object_pos_start":[0.50602,0.06299,0.0338],"object_to_goal_dist_end":0.13889,"object_to_goal_dist_start":0.14325,"object_z_max":0.03679,"peak_contact_force":0.0,"phase_name":"align_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14.0,"raw_peak_contact_force":42.03112,"subtask_id":"reach_peg","tcp_end":[0.50318,0.08797,0.04188],"tcp_start":[0.52032,0.15745,0.21404],"tcp_to_object_dist_end":0.02989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50636,0.05454,0.03606],"object_pos_start":[0.5065,0.0587,0.03685],"object_to_goal_dist_end":0.13475,"object_to_goal_dist_start":0.13889,"object_z_max":0.03687,"peak_contact_force":0.53411,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":146.0,"raw_peak_contact_force":3.88411,"subtask_id":"push_to_exit","tcp_end":[0.50193,0.08303,0.04037],"tcp_start":[0.50198,0.08349,0.04046],"tcp_to_object_dist_end":0.02915,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81013,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_peg.align_speed":0.0861,"align_behind_peg.align_tolerance":0.0124,"approach_overhead.overhead_speed":0.21319,"approach_overhead.overhead_tolerance":0.03104,"push_through_channel.contact_force_threshold":6.0931,"push_through_channel.push_distance":0.20063,"push_through_channel.push_speed":0.12317,"push_through_channel.push_tolerance":0.04205},"optimized_scores":{"best_composite_score":-0.31787,"best_fitness_score":0.11213,"best_task_score":0.01686},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50353,0.03527,0.00993],"force_p95":41.48391,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.74122,"mean_force":14.99278,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50279,0.07905,0.04083]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50448,0.06826,0.04038],"force_p95":26.36877,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.72115,"mean_force":5.73035,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50298,0.08005,0.04101]},{"body_a":"peg","body_b":"channel_base_body","contact_count":562.0,"contact_point_centroid":[0.50613,0.05541,0.00939],"force_p95":0.60199,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.00188,"mean_force":0.70585,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"descend","tcp_position_centroid":[0.51372,0.11677,0.12573]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50527,0.0721,0.04788],"force_p95":14.65939,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.69458,"mean_force":10.67762,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"descend","tcp_position_centroid":[0.50433,0.08401,0.0477]},{"body_a":"peg","body_b":"channel_base_body","contact_count":118.0,"contact_point_centroid":[0.50481,0.05673,0.00927],"force_p95":1.44326,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.68152,"phase_index":0.0,"phase_name":"approach_overhead","phase_type":"approach","tcp_position_centroid":[0.51452,0.17254,0.24911]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_overhead","phase_type":"approach","tcp_position_centroid":[0.50216,0.19572,0.29178]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52503,0.05517,0.05895],"force_p95":1.633,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81015,"mean_force":0.62598,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"descend","tcp_position_centroid":[0.50473,0.08538,0.051]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.0536,0.01289],"force_p95":1.25077,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25077,"mean_force":1.25077,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50286,0.08046,0.0409]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.08158,0.06],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50356,0.08151,0.04167]}],"total_contact_groups":9},"final_pose_error":0.1955,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50581,0.04688,0.03725],"final_tcp_position":[0.50242,0.07642,0.04027],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":47.74122,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":147.0,"n_steps_budget":600.0,"object_pos_end":[0.50616,0.0566,0.03376],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.0,"phase_name":"approach_overhead","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":574.0,"raw_peak_contact_force":15.00188,"subtask_id":"reach_peg","tcp_end":[0.52572,0.15216,0.2128],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.50659,0.05245,0.03693],"object_pos_start":[0.50616,0.0566,0.03376],"object_to_goal_dist_end":0.13265,"object_to_goal_dist_start":0.13688,"object_z_max":0.03685,"peak_contact_force":0.0,"phase_name":"align_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18.0,"raw_peak_contact_force":47.74122,"subtask_id":"reach_peg","tcp_end":[0.50363,0.08155,0.04177],"tcp_start":[0.52572,0.15216,0.2128],"tcp_to_object_dist_end":0.02965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.04807,0.03694],"object_pos_start":[0.50659,0.05245,0.03693],"object_to_goal_dist_end":0.12825,"object_to_goal_dist_start":0.13265,"object_z_max":0.03723,"peak_contact_force":0.59447,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":155.0,"raw_peak_contact_force":4.44541,"subtask_id":"push_to_exit","tcp_end":[0.50242,0.07642,0.04027],"tcp_start":[0.50246,0.0769,0.04035],"tcp_to_object_dist_end":0.02876,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15254,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_peg.align_speed":0.16681,"align_behind_peg.align_tolerance":0.01111,"approach_overhead.overhead_speed":0.27708,"approach_overhead.overhead_tolerance":0.0351,"push_through_channel.contact_force_threshold":5.98838,"push_through_channel.push_distance":0.20838,"push_through_channel.push_speed":0.10689,"push_through_channel.push_tolerance":0.05972},"optimized_scores":{"best_composite_score":-0.2898,"best_fitness_score":0.1402,"best_task_score":0.01853},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":536.0,"contact_point_centroid":[0.494,0.07882,0.00939],"force_p95":0.57938,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.03404,"mean_force":0.67628,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"descend","tcp_position_centroid":[0.48193,0.13767,0.12886]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.49407,0.09416,0.05281],"force_p95":12.1427,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.54022,"mean_force":4.41853,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"descend","tcp_position_centroid":[0.48852,0.10568,0.04564]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.48863,0.06246,0.00931],"force_p95":7.99833,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.86795,"mean_force":2.51645,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48767,0.09993,0.03992]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49807,0.09102,0.05993],"force_p95":8.17439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.72274,"mean_force":2.08665,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48828,0.10256,0.04055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":99.0,"contact_point_centroid":[0.49521,0.08009,0.0093],"force_p95":1.32425,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.67505,"phase_index":0.0,"phase_name":"approach_overhead","phase_type":"approach","tcp_position_centroid":[0.48668,0.18278,0.25072]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_overhead","phase_type":"approach","tcp_position_centroid":[0.49758,0.19697,0.29179]}],"total_contact_groups":6},"final_pose_error":0.20074,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50204,0.06865,0.03482],"final_tcp_position":[0.48752,0.09631,0.0395],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":15.03404,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":127.0,"n_steps_budget":600.0,"object_pos_end":[0.4938,0.07995,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.11316,"phase_name":"approach_overhead","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":553.0,"raw_peak_contact_force":15.03404,"subtask_id":"reach_peg","tcp_end":[0.47733,0.17054,0.21639],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":750.0,"object_pos_end":[0.49839,0.07483,0.03739],"object_pos_start":[0.4938,0.07995,0.03378],"object_to_goal_dist_end":0.15486,"object_to_goal_dist_start":0.16019,"object_z_max":0.03771,"peak_contact_force":1.18812,"phase_name":"align_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17.0,"raw_peak_contact_force":9.86795,"subtask_id":"reach_peg","tcp_end":[0.48881,0.10396,0.0412],"tcp_start":[0.47733,0.17054,0.21639],"tcp_to_object_dist_end":0.03091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.50114,0.06981,0.03461],"object_pos_start":[0.49839,0.07483,0.03739],"object_to_goal_dist_end":0.14991,"object_to_goal_dist_start":0.15486,"object_z_max":0.03739,"peak_contact_force":0.50465,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":134.0,"raw_peak_contact_force":3.77147,"subtask_id":"push_to_exit","tcp_end":[0.48752,0.09631,0.0395],"tcp_start":[0.4875,0.09687,0.03959],"tcp_to_object_dist_end":0.03019,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```