## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.0716 | 0.59 | ❌ rejected |
| 10 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.2820 | 0.70 | ✅ accepted |
| 9 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0732 | 0.01 | ❌ rejected |
| 8 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.1539 | 0.61 | ❌ rejected |
| 7 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0616 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.59 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.072) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: align_to_entry
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.15
    - 0.04
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.06
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
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
    - 0.01
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 4.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_through
  type: push
  generator: impedance_motion
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
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_threshold:
      type: scalar
      range:
      - 20.0
      - 38.0
      default: 30.0
      binds_to:
      - path: guards.push_contact.threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_contact
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_to_entry** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.15, 0.04]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_threshold: status=consumed; consumers=guards.push_contact.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_contact, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.072
- **task_score** (E): 0.589
- **fitness_score**: 0.548  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_entry | 1.00 | 1.00 | 0.2573 |
| approach_peg | 1.00 | 1.00 | 0.0214 |
| contact_peg | 0.67 | 1.00 | 0.0386 |
| push_through | 0.33 | 1.00 | 0.0584 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_entry | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.168, 0.045) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.533 | 2.732 |
| approach_peg | approach | 1.00 / step_budget | (0.496, 0.168, 0.045)→(0.498, 0.153, 0.036) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.538 | 0.585 |
| contact_peg | contact | 0.67 / step_budget | (0.498, 0.153, 0.036)→(0.497, 0.115, 0.029) | (0.502, 0.098, 0.034)→(0.504, 0.086, 0.035) | 0.178→0.166 | 1.00 / 2.333 | 1307.732 | 4.029 |
| push_through | push | 0.33 / guard_failure | (0.498, 0.025, 0.029)→(0.500, -0.034, 0.030) | (0.504, 0.086, 0.035)→(0.506, -0.062, 0.036) | 0.166→0.024 | 1.00 / 2.333 | 3.190 | 31.210 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.687
- terminal_score: 0.990
- phase_score: 0.603
- phase_breakdown.approach_score: 0.727
- phase_breakdown.contact_score: 0.722
- phase_breakdown.push_score: 0.523

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.758
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.990
- **Median Q (composite search score)**: 0.162
- **K-run variance**: 0.0236
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.300


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91262,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.04544,"align_to_entry.speed":0.12118,"approach_peg.approach_tolerance":0.01387,"approach_peg.speed":0.03708,"contact_peg.contact_force":5.78929,"contact_peg.speed":0.01962,"push_through.push_distance":0.15691,"push_through.push_force_threshold":29.57693,"push_through.push_speed":0.03753,"push_through.push_tolerance":0.0131},"optimized_scores":{"best_composite_score":0.19782,"best_fitness_score":0.75782,"best_task_score":0.9895},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.5055,-0.01199,0.00989],"force_p95":12.13193,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.6689,"mean_force":4.49732,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49942,0.03275,0.02833]},{"body_a":"attachment","body_b":"peg","contact_count":575.0,"contact_point_centroid":[0.50371,0.02769,0.04288],"force_p95":11.63359,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.87193,"mean_force":2.98386,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49915,0.03935,0.02814]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":412.0,"contact_point_centroid":[0.5251,0.02331,0.02644],"force_p95":5.96685,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.59112,"mean_force":1.41752,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49864,0.0521,0.0278]},{"body_a":"attachment","body_b":"peg","contact_count":477.0,"contact_point_centroid":[0.50206,0.12186,0.04238],"force_p95":2.365,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.75527,"mean_force":1.67122,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49767,0.13354,0.03069]},{"body_a":"peg","body_b":"channel_base_body","contact_count":964.0,"contact_point_centroid":[0.50492,0.10008,0.00966],"force_p95":2.43077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.14488,"mean_force":1.23912,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49637,0.14213,0.03199]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":133.0,"contact_point_centroid":[0.52506,0.09907,0.03223],"force_p95":1.271,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36287,"mean_force":0.88663,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4986,0.12795,0.02996]},{"body_a":"peg","body_b":"channel_base_body","contact_count":832.0,"contact_point_centroid":[0.5036,0.11162,0.00939],"force_p95":0.61125,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55337,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49772,0.20417,0.16751]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.50353,0.11294,0.00943],"force_p95":0.5861,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59766,"mean_force":0.5454,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49636,0.15864,0.04204]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49984,0.19981,0.29891]}],"total_contact_groups":9},"final_pose_error":0.01293,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5048,-0.07923,0.03555],"final_tcp_position":[0.50276,-0.04907,0.03057],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":15.6689,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11176,0.03389],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5057,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":848.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49637,0.15814,0.04444],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":31.0,"n_steps_budget":600.0,"object_pos_end":[0.5037,0.11175,0.03385],"object_pos_start":[0.50372,0.11176,0.03389],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.1919,"object_z_max":0.03389,"peak_contact_force":0.54845,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31.0,"raw_peak_contact_force":0.59766,"subtask_id":"approach","tcp_end":[0.49703,0.16099,0.03896],"tcp_start":[0.49637,0.15814,0.04444],"tcp_to_object_dist_end":0.04995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50704,0.09673,0.03559],"object_pos_start":[0.5037,0.11175,0.03385],"object_to_goal_dist_end":0.17693,"object_to_goal_dist_start":0.19188,"object_z_max":0.03568,"peak_contact_force":2.4306,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1574.0,"raw_peak_contact_force":3.75527,"subtask_id":"contact","tcp_end":[0.49894,0.12584,0.02967],"tcp_start":[0.49703,0.16099,0.03896],"tcp_to_object_dist_end":0.03079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.5048,-0.07923,0.03555],"object_pos_start":[0.50704,0.09673,0.03559],"object_to_goal_dist_end":0.00659,"object_to_goal_dist_start":0.17693,"object_z_max":0.03609,"peak_contact_force":1.44485,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1347.0,"raw_peak_contact_force":15.6689,"subtask_id":"push","tcp_end":[0.50276,-0.04907,0.03057],"tcp_start":[0.49894,0.12584,0.02967],"tcp_to_object_dist_end":0.03064,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28049,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.0768,"align_to_entry.speed":0.13533,"approach_peg.approach_tolerance":0.01978,"approach_peg.speed":0.0774,"contact_peg.contact_force":5.79199,"contact_peg.speed":0.0253,"push_through.push_distance":0.14339,"push_through.push_force_threshold":31.94199,"push_through.push_speed":0.04205,"push_through.push_tolerance":0.02316},"optimized_scores":{"best_composite_score":-0.14489,"best_fitness_score":0.41511,"best_task_score":0.39858},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":178.0,"contact_point_centroid":[0.52521,0.02849,0.03113],"force_p95":12.47193,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.29285,"mean_force":3.00072,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49194,0.05462,0.0279]},{"body_a":"attachment","body_b":"peg","contact_count":223.0,"contact_point_centroid":[0.49892,0.05705,0.04173],"force_p95":22.7329,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.02431,"mean_force":4.84915,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49175,0.06773,0.02788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":102.0,"contact_point_centroid":[0.50501,0.02989,0.0099],"force_p95":21.56942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.3859,"mean_force":8.38668,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49173,0.07267,0.02796]},{"body_a":"peg","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.52063,0.07796,0.06295],"force_p95":13.4231,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.11116,"mean_force":1.82699,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49079,0.09563,0.02707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":620.0,"contact_point_centroid":[0.49632,0.10123,0.00979],"force_p95":3.00219,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.8453,"mean_force":1.74662,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49216,0.14441,0.03117]},{"body_a":"attachment","body_b":"peg","contact_count":447.0,"contact_point_centroid":[0.49515,0.12797,0.04059],"force_p95":2.84715,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.52227,"mean_force":1.86755,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.492,0.13981,0.03039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":905.0,"contact_point_centroid":[0.49618,0.11917,0.00941],"force_p95":0.60179,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55076,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49777,0.22271,0.16172]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.50019,0.20003,0.29779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49277,0.11942,0.00946],"force_p95":0.59903,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60353,"mean_force":0.54461,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49587,0.15912,0.03861]}],"total_contact_groups":9},"final_pose_error":0.04552,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50756,-0.02583,0.03685],"final_tcp_position":[0.49351,0.00256,0.02913],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":33.29285,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11898,0.034],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54496,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":929.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.49631,0.15914,0.03973],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49606,0.11918,0.03389],"object_pos_start":[0.496,0.11898,0.034],"object_to_goal_dist_end":0.19931,"object_to_goal_dist_start":0.19911,"object_z_max":0.034,"peak_contact_force":0.51922,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":0.60353,"subtask_id":"approach","tcp_end":[0.49541,0.16073,0.03718],"tcp_start":[0.49631,0.15914,0.03973],"tcp_to_object_dist_end":0.04169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":658.0,"n_steps_budget":810.0,"object_pos_end":[0.49901,0.10121,0.03543],"object_pos_start":[0.49606,0.11918,0.03389],"object_to_goal_dist_end":0.18127,"object_to_goal_dist_start":0.19931,"object_z_max":0.03547,"peak_contact_force":1.73658,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1067.0,"raw_peak_contact_force":4.8453,"subtask_id":"contact","tcp_end":[0.49218,0.13062,0.02946],"tcp_start":[0.49541,0.16073,0.03718],"tcp_to_object_dist_end":0.03078,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.50767,-0.02443,0.03689],"object_pos_start":[0.49901,0.10121,0.03543],"object_to_goal_dist_end":0.05618,"object_to_goal_dist_start":0.18127,"object_z_max":0.03726,"peak_contact_force":2.03382,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":544.0,"raw_peak_contact_force":33.29285,"subtask_id":"push","tcp_end":[0.49351,0.00256,0.02913],"tcp_start":[0.49356,0.00274,0.0292],"tcp_to_object_dist_end":0.03145,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17131,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.08434,"align_to_entry.speed":0.06363,"approach_peg.approach_tolerance":0.01457,"approach_peg.speed":0.0752,"contact_peg.contact_force":6.58353,"contact_peg.speed":0.02893,"push_through.push_distance":0.14586,"push_through.push_force_threshold":35.76997,"push_through.push_speed":0.02475,"push_through.push_tolerance":0.02468},"optimized_scores":{"best_composite_score":0.16175,"best_fitness_score":0.47175,"best_task_score":0.37758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":258.0,"contact_point_centroid":[0.5045,0.00997,0.04293],"force_p95":23.91208,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.66828,"mean_force":5.26874,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50005,0.02162,0.02747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50713,-0.10045,0.06151],"force_p95":41.38591,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.38659,"mean_force":23.53859,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50233,-0.05417,0.02942]},{"body_a":"peg","body_b":"channel_base_body","contact_count":100.0,"contact_point_centroid":[0.50507,-0.02394,0.00988],"force_p95":22.32669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.39348,"mean_force":6.44332,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50017,0.02025,0.02762]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":215.0,"contact_point_centroid":[0.52524,-0.00256,0.03086],"force_p95":21.87288,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.95098,"mean_force":4.13803,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49984,0.02664,0.02727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49771,0.23305,0.17774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":907.0,"contact_point_centroid":[0.50598,0.061,0.00943],"force_p95":2.28354,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.48629,"mean_force":0.70934,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49884,0.11024,0.02874]},{"body_a":"attachment","body_b":"peg","contact_count":90.0,"contact_point_centroid":[0.50416,0.07866,0.04184],"force_p95":2.87471,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.19342,"mean_force":1.852,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50046,0.09052,0.02885]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.50018,0.19992,0.29741]},{"body_a":"peg","body_b":"channel_base_body","contact_count":165.0,"contact_point_centroid":[0.50577,0.06327,0.00938],"force_p95":0.55146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55424,"mean_force":0.54659,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4974,0.16224,0.0413]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.525,0.05959,0.01043],"force_p95":0.41093,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42375,"mean_force":0.31773,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50066,0.08852,0.0289]}],"total_contact_groups":10},"final_pose_error":0.03326,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50691,-0.0835,0.03655],"final_tcp_position":[0.50227,-0.05478,0.02933],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3919.03,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49638,0.18753,0.05168],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":165.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06301,0.03381],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":0.54685,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":165.0,"raw_peak_contact_force":0.55424,"subtask_id":"approach","tcp_end":[0.50026,0.13617,0.03293],"tcp_start":[0.49638,0.18753,0.05168],"tcp_to_object_dist_end":0.0734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":915.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,0.05872,0.0354],"object_pos_start":[0.50603,0.06301,0.03381],"object_to_goal_dist_end":0.13897,"object_to_goal_dist_start":0.14327,"object_z_max":0.03544,"peak_contact_force":3919.03,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1000.0,"raw_peak_contact_force":3.48629,"subtask_id":"contact","tcp_end":[0.50069,0.08817,0.02891],"tcp_start":[0.50026,0.13617,0.03293],"tcp_to_object_dist_end":0.03081,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,-0.08257,0.03666],"object_pos_start":[0.50701,0.05872,0.0354],"object_to_goal_dist_end":0.00813,"object_to_goal_dist_start":0.13897,"object_z_max":0.03669,"peak_contact_force":6.09058,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":577.0,"raw_peak_contact_force":44.66828,"subtask_id":"push","tcp_end":[0.50227,-0.05478,0.02933],"tcp_start":[0.50229,-0.05461,0.02938],"tcp_to_object_dist_end":0.02912,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```