## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3139 | 0.77 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3307 | 0.46 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3411 | 0.65 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1002 | 0.12 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3662 | 0.39 | ❌ rejected |

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
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=0.314) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.3
- id: push_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_behind
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
    - 0.02
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
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
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  guards:
  - id: check_approach
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: pre_push
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
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: ensure_contact
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
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
      distance: 0.18
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: push_goal
- id: retract
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
    retract_speed:
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
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
  - guards:
    - id=check_approach, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=ensure_contact, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.314
- **task_score** (E): 0.773
- **fitness_score**: 0.674  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 0.00 | 1.00 | 0.0742 |
| contact_peg | 0.00 | 1.00 | 0.0301 |
| push_channel | 0.00 | 1.00 | 0.1319 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 0.00 / step_budget | (0.494, 0.141, 0.107)→(0.499, 0.121, 0.036) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.667 | 0.795 | 66.484 |
| contact_peg | contact | 0.00 / step_budget | (0.499, 0.121, 0.036)→(0.499, 0.092, 0.031) | (0.503, 0.091, 0.036)→(0.502, 0.063, 0.035) | 0.171→0.143 | 1.00 / 2.333 | 1.153 | 3.849 |
| push_channel | push | 0.00 / guard_failure | (0.499, 0.092, 0.031)→(0.493, -0.040, 0.032) | (0.502, 0.063, 0.035)→(0.504, -0.066, 0.036) | 0.143→0.024 | 1.00 / 2.667 | 27.114 | 40.502 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.694
- phase_breakdown.pre_push_score: 0.931
- phase_breakdown.push_goal_score: 0.593

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.817
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.432
- **K-run variance**: 0.0340
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.234


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06548,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06438,"approach_behind.lateral_offset_x":-7e-05,"contact_peg.contact_force_threshold":8.57924,"contact_peg.contact_speed":0.02019,"push_channel.push_speed":0.04961,"retract.retract_speed":0.02842},"optimized_scores":{"best_composite_score":0.43161,"best_fitness_score":0.79161,"best_task_score":0.91761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":632.0,"contact_point_centroid":[0.49715,-0.01626,0.03466],"force_p95":29.42704,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.99147,"mean_force":4.06277,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49633,-0.00434,0.02866]},{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.49698,-0.10159,0.03812],"force_p95":39.40128,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.74717,"mean_force":26.7234,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49692,-0.05573,0.03073]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1499.0,"contact_point_centroid":[0.50316,0.06593,0.0094],"force_p95":0.80466,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.0169,"mean_force":0.8249,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49887,0.14152,0.16084]},{"body_a":"attachment","body_b":"peg","contact_count":73.0,"contact_point_centroid":[0.50318,0.08142,0.04704],"force_p95":13.44923,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.90093,"mean_force":5.87031,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50261,0.0934,0.04446]},{"body_a":"peg","body_b":"channel_base_body","contact_count":537.0,"contact_point_centroid":[0.49673,-0.03478,0.00993],"force_p95":2.83685,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.54092,"mean_force":1.27192,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49628,0.00356,0.02839]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.4984,0.03629,0.0098],"force_p95":1.18153,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.20762,"mean_force":0.71073,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49948,0.07364,0.03024]},{"body_a":"attachment","body_b":"peg","contact_count":608.0,"contact_point_centroid":[0.4991,0.06106,0.03067],"force_p95":0.83706,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.72864,"mean_force":0.43325,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49941,0.07304,0.03017]}],"total_contact_groups":7},"final_pose_error":0.06044,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49691,-0.08798,0.03527],"final_tcp_position":[0.49702,-0.05878,0.03082],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":40.99147,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1519.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54698,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1572.0,"raw_peak_contact_force":16.0169,"subtask_id":"pre_push","tcp_end":[0.50351,0.08932,0.03478],"tcp_start":[0.49869,0.12291,0.11919],"tcp_to_object_dist_end":0.02192,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":739.0,"n_steps_budget":930.0,"object_pos_end":[0.49826,0.03123,0.03473],"object_pos_start":[0.5029,0.0595,0.03455],"object_to_goal_dist_end":0.11137,"object_to_goal_dist_start":0.13964,"object_z_max":0.03479,"peak_contact_force":0.69684,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1347.0,"raw_peak_contact_force":2.20762,"tcp_end":[0.49897,0.06122,0.02987],"tcp_start":[0.50351,0.08932,0.03478],"tcp_to_object_dist_end":0.03038,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":770.0,"n_steps_budget":1000.0,"object_pos_end":[0.49691,-0.08798,0.03527],"object_pos_start":[0.49826,0.03123,0.03473],"object_to_goal_dist_end":0.00978,"object_to_goal_dist_start":0.11137,"object_z_max":0.03536,"peak_contact_force":40.99147,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1248.0,"raw_peak_contact_force":40.99147,"subtask_id":"push_goal","tcp_end":[0.49702,-0.05878,0.03082],"tcp_start":[0.49897,0.06122,0.02987],"tcp_to_object_dist_end":0.02954,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01961,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.0669,"approach_behind.lateral_offset_x":0.00122,"contact_peg.contact_force_threshold":15.09392,"contact_peg.contact_speed":0.01924,"push_channel.push_speed":0.04044,"retract.retract_speed":0.05684},"optimized_scores":{"best_composite_score":0.45652,"best_fitness_score":0.81652,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1449.0,"contact_point_centroid":[0.50527,0.11211,0.00927],"force_p95":120.17757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":145.55924,"mean_force":13.53632,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50311,0.16295,0.15559]},{"body_a":"attachment","body_b":"peg","contact_count":187.0,"contact_point_centroid":[0.51513,0.12888,0.05474],"force_p95":144.15375,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":144.95883,"mean_force":100.70752,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50939,0.13884,0.05358]},{"body_a":"attachment","body_b":"peg","contact_count":804.0,"contact_point_centroid":[0.50194,0.0065,0.04285],"force_p95":9.21365,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.34705,"mean_force":3.38252,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49706,0.01802,0.03193]},{"body_a":"peg","body_b":"channel_base_body","contact_count":27.0,"contact_point_centroid":[0.5071,-0.10037,0.06027],"force_p95":33.39483,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.9748,"mean_force":25.64672,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49631,-0.05394,0.03403]},{"body_a":"peg","body_b":"channel_base_body","contact_count":497.0,"contact_point_centroid":[0.50533,-0.01864,0.00992],"force_p95":8.10552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.33527,"mean_force":4.13023,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49722,0.02546,0.0318]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":524.0,"contact_point_centroid":[0.52506,-0.01451,0.02531],"force_p95":3.39489,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77684,"mean_force":1.10314,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49688,0.01335,0.0319]},{"body_a":"peg","body_b":"channel_base_body","contact_count":870.0,"contact_point_centroid":[0.50109,0.07519,0.0099],"force_p95":1.41449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.52387,"mean_force":0.81253,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50288,0.11538,0.03339]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":62.0,"contact_point_centroid":[0.52533,0.11299,0.0506],"force_p95":3.14089,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.17052,"mean_force":1.87579,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50926,0.15469,0.11411]},{"body_a":"attachment","body_b":"peg","contact_count":754.0,"contact_point_centroid":[0.50252,0.10309,0.03419],"force_p95":1.0794,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.16076,"mean_force":0.54665,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50282,0.11506,0.03336]}],"total_contact_groups":9},"final_pose_error":0.02456,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50718,-0.08218,0.03598],"final_tcp_position":[0.49621,-0.05485,0.03397],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":145.55924,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1471.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11176,0.03395],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.43469,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1698.0,"raw_peak_contact_force":145.55924,"subtask_id":"pre_push","tcp_end":[0.50849,0.13422,0.03786],"tcp_start":[0.50479,0.14917,0.10535],"tcp_to_object_dist_end":0.02329,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.50107,0.07148,0.03492],"object_pos_start":[0.50504,0.10006,0.03833],"object_to_goal_dist_end":0.15157,"object_to_goal_dist_start":0.18014,"object_z_max":0.03834,"peak_contact_force":1.36844,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1624.0,"raw_peak_contact_force":3.52387,"tcp_end":[0.50132,0.10144,0.03348],"tcp_start":[0.50849,0.13422,0.03786],"tcp_to_object_dist_end":0.02999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.50718,-0.08218,0.03598],"object_pos_start":[0.50107,0.07148,0.03492],"object_to_goal_dist_end":0.00851,"object_to_goal_dist_start":0.15157,"object_z_max":0.03626,"peak_contact_force":40.34705,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1852.0,"raw_peak_contact_force":40.34705,"subtask_id":"push_goal","tcp_end":[0.49621,-0.05485,0.03397],"tcp_start":[0.50132,0.10144,0.03348],"tcp_to_object_dist_end":0.02952,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98953,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06422,"approach_behind.lateral_offset_x":-0.0096,"contact_peg.contact_force_threshold":14.43397,"contact_peg.contact_speed":0.01719,"push_channel.push_speed":0.04033,"retract.retract_speed":0.08523},"optimized_scores":{"best_composite_score":0.05344,"best_fitness_score":0.41344,"best_task_score":0.40072},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.475,-0.00247,0.03159],"force_p95":37.45258,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.16823,"mean_force":28.70946,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48682,-0.00247,0.02958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1379.0,"contact_point_centroid":[0.49719,0.11693,0.00947],"force_p95":0.78832,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.87531,"mean_force":0.884,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48615,0.16627,0.15528]},{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.49102,0.13149,0.05561],"force_p95":29.89904,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.4424,"mean_force":7.22126,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48412,0.14192,0.04704]},{"body_a":"attachment","body_b":"peg","contact_count":608.0,"contact_point_centroid":[0.49738,0.03981,0.03638],"force_p95":13.7471,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.14088,"mean_force":5.86173,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48932,0.04961,0.02842]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":594.0,"contact_point_centroid":[0.52516,0.02314,0.02754],"force_p95":11.52841,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.97978,"mean_force":3.82653,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48921,0.04693,0.02851]},{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.5071,0.00824,0.00995],"force_p95":10.46362,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.79216,"mean_force":5.98643,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48929,0.04811,0.0285]},{"body_a":"peg","body_b":"link7","contact_count":60.0,"contact_point_centroid":[0.51961,-0.0156,0.06473],"force_p95":10.20192,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.39362,"mean_force":4.33701,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48685,-0.00158,0.02954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":808.0,"contact_point_centroid":[0.50816,0.0839,0.00998],"force_p95":3.15612,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.81638,"mean_force":1.99356,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48977,0.12535,0.03086]},{"body_a":"attachment","body_b":"peg","contact_count":861.0,"contact_point_centroid":[0.49785,0.1141,0.04471],"force_p95":4.48991,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.53931,"mean_force":2.31142,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49004,0.12469,0.03081]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":575.0,"contact_point_centroid":[0.52516,0.09394,0.04198],"force_p95":3.63659,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.8335,"mean_force":2.03432,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49197,0.12068,0.03075]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49947,0.19931,0.29846]}],"total_contact_groups":11},"final_pose_error":0.06102,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50773,-0.02788,0.03792],"final_tcp_position":[0.48684,-0.00546,0.0298],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":40.16823,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1417.0,"n_steps_budget":1000.0,"object_pos_end":[0.49598,0.11916,0.03409],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":1.40358,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1470.0,"raw_peak_contact_force":37.87531,"subtask_id":"pre_push","tcp_end":[0.48646,0.13933,0.03475],"tcp_start":[0.47861,0.15194,0.09522],"tcp_to_object_dist_end":0.02232,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":912.0,"n_steps_budget":1000.0,"object_pos_end":[0.50725,0.08547,0.03599],"object_pos_start":[0.50066,0.11262,0.03593],"object_to_goal_dist_end":0.16568,"object_to_goal_dist_start":0.19266,"object_z_max":0.03666,"peak_contact_force":1.39434,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2244.0,"raw_peak_contact_force":5.81638,"tcp_end":[0.49576,0.11356,0.03104],"tcp_start":[0.48646,0.13933,0.03475],"tcp_to_object_dist_end":0.03075,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":717.0,"n_steps_budget":1000.0,"object_pos_end":[0.50773,-0.02788,0.03792],"object_pos_start":[0.50725,0.08547,0.03599],"object_to_goal_dist_end":0.05273,"object_to_goal_dist_start":0.16568,"object_z_max":0.03791,"peak_contact_force":0.00286,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1715.0,"raw_peak_contact_force":40.16823,"subtask_id":"push_goal","tcp_end":[0.48684,-0.00546,0.0298],"tcp_start":[0.49576,0.11356,0.03104],"tcp_to_object_dist_end":0.0317,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```