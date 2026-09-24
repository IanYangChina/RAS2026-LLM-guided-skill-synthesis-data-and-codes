## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → contact → push → retract | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1187 | 0.64 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1087 | 0.61 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3597 | 0.68 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3139 | 0.77 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3307 | 0.46 | ❌ rejected |

**Proposal policy**: task_score is 0.64 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.119) — your mutation base

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

- **Composite score**: 0.119
- **task_score** (E): 0.638
- **fitness_score**: 0.542  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 0.00 | 1.00 | 0.0754 |
| align_tool | 1.00 | 1.00 | 0.0259 |
| contact_peg | 1.00 | 1.00 | 0.0276 |
| push_channel | 0.33 | 1.00 | 0.0491 |
| retract | 1.00 | 1.00 | 0.0907 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 0.00 / step_budget | (0.498, 0.142, 0.109)→(0.503, 0.123, 0.037) | (0.500, 0.099, 0.040)→(0.501, 0.101, 0.034) | 0.180→0.181 | 1.00 / 1.667 | 157.331 | 216.870 |
| align_tool | align | 1.00 / step_budget | (0.503, 0.123, 0.037)→(0.493, 0.147, 0.033) | (0.500, 0.109, 0.028)→(0.495, 0.113, 0.027) | 0.190→0.194 | 1.00 / 1.333 | 16.181 | 41.123 |
| contact_peg | contact | 1.00 / step_budget | (0.493, 0.147, 0.033)→(0.491, 0.120, 0.030) | (0.495, 0.113, 0.027)→(0.496, 0.101, 0.028) | 0.194→0.182 | 1.00 / 2.000 | 18.172 | 19.676 |
| push_channel | push | 0.33 / guard_failure | (0.488, 0.076, 0.030)→(0.486, 0.028, 0.030) | (0.496, 0.101, 0.028)→(0.499, 0.012, 0.029) | 0.182→0.097 | 1.00 / 2.667 | 24.278 | 46.310 |
| retract | retract | 1.00 / step_budget | (0.486, 0.028, 0.030)→(0.483, 0.027, 0.120) | (0.499, 0.012, 0.029)→(0.492, 0.012, 0.027) | 0.097→0.095 | 1.00 / 1.000 | 0.569 | 145.596 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.915
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.915
- phase_score: 0.657
- phase_breakdown.pre_push_score: 0.841
- phase_breakdown.push_goal_score: 0.579

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.761
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.222
- **K-run variance**: 0.0330
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.280


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91538,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.05657,"approach_behind.lateral_offset_x":0.00806,"contact_peg.contact_force_threshold":11.07338,"contact_peg.contact_speed":0.02326,"push_channel.max_push_force":39.97881,"push_channel.push_offset_x":0.00125,"push_channel.push_speed":0.04632,"retract.retract_speed":0.03103},"optimized_scores":{"best_composite_score":0.27059,"best_fitness_score":0.76059,"best_task_score":0.91547},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":93.0,"contact_point_centroid":[0.5252,0.09249,0.05997],"force_p95":509.40662,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":537.02661,"mean_force":382.35524,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51051,0.0926,0.04127]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":149.0,"contact_point_centroid":[0.475,-0.0562,0.04744],"force_p95":108.07399,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.58548,"mean_force":55.68239,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48676,-0.05621,0.04509]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52508,0.09251,0.05999],"force_p95":74.1114,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.61283,"mean_force":59.19638,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.5099,0.09261,0.03958]},{"body_a":"attachment","body_b":"peg","contact_count":698.0,"contact_point_centroid":[0.49925,-0.00745,0.04053],"force_p95":13.86,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.68643,"mean_force":6.09764,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49162,0.00313,0.02776]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.50722,-0.10038,0.05997],"force_p95":35.17353,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.44864,"mean_force":25.37646,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49001,-0.05589,0.02957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":100.0,"contact_point_centroid":[0.50671,-0.10018,0.06045],"force_p95":13.82221,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.97859,"mean_force":5.89354,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48735,-0.05624,0.03388]},{"body_a":"attachment","body_b":"peg","contact_count":239.0,"contact_point_centroid":[0.49605,-0.06637,0.05793],"force_p95":12.82258,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.48419,"mean_force":2.65909,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48697,-0.05629,0.04419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1584.0,"contact_point_centroid":[0.50273,0.06664,0.00937],"force_p95":0.58434,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.96868,"mean_force":0.61443,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50311,0.14133,0.16005]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.5068,0.08235,0.04521],"force_p95":7.77178,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.89273,"mean_force":2.61655,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51012,0.09384,0.04477]},{"body_a":"peg","body_b":"channel_base_body","contact_count":509.0,"contact_point_centroid":[0.50646,-0.03114,0.00995],"force_p95":10.83872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.7529,"mean_force":5.71046,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49184,0.01119,0.02753]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":598.0,"contact_point_centroid":[0.52509,-0.02448,0.03305],"force_p95":8.52226,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.09881,"mean_force":3.07587,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49144,0.00157,0.02767]},{"body_a":"peg","body_b":"link7","contact_count":164.0,"contact_point_centroid":[0.52148,0.02128,0.06203],"force_p95":8.2321,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.99316,"mean_force":4.22922,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49234,0.03918,0.02641]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52507,-0.08222,0.05785],"force_p95":4.52982,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.40092,"mean_force":2.29533,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48733,-0.0562,0.03276]},{"body_a":"peg","body_b":"channel_base_body","contact_count":954.0,"contact_point_centroid":[0.50065,0.04916,0.00968],"force_p95":2.62273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.41632,"mean_force":1.31482,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49726,0.09204,0.02989]},{"body_a":"attachment","body_b":"peg","contact_count":535.0,"contact_point_centroid":[0.49983,0.07107,0.04031],"force_p95":2.46918,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.09258,"mean_force":1.57059,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49692,0.08293,0.02953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":821.0,"contact_point_centroid":[0.50656,-0.0834,0.00959],"force_p95":0.62097,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.99428,"mean_force":0.54177,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48638,-0.05655,0.07769]}],"total_contact_groups":18},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50272,-0.07901,0.03379],"final_tcp_position":[0.48638,-0.0567,0.11991],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":537.02661,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1608.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":471.16392,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1717.0,"raw_peak_contact_force":537.02661,"subtask_id":"pre_push","tcp_end":[0.51001,0.09258,0.03971],"tcp_start":[0.50385,0.1269,0.12835],"tcp_to_object_dist_end":0.02675,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":298.0,"n_steps_budget":600.0,"object_pos_end":[0.50056,0.06381,0.03382],"object_pos_start":[0.50092,0.06403,0.03389],"object_to_goal_dist_end":0.14395,"object_to_goal_dist_start":0.14416,"object_z_max":0.03402,"peak_contact_force":0.54467,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":306.0,"raw_peak_contact_force":74.61283,"tcp_end":[0.50135,0.11467,0.0348],"tcp_start":[0.51001,0.09258,0.03971],"tcp_to_object_dist_end":0.05087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50252,0.04269,0.03531],"object_pos_start":[0.50056,0.06381,0.03382],"object_to_goal_dist_end":0.1228,"object_to_goal_dist_start":0.14395,"object_z_max":0.03532,"peak_contact_force":2.35155,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1489.0,"raw_peak_contact_force":4.41632,"tcp_end":[0.49676,0.07222,0.02936],"tcp_start":[0.50135,0.11467,0.0348],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.50736,-0.08145,0.03642],"object_pos_start":[0.50252,0.04269,0.03531],"object_to_goal_dist_end":0.00831,"object_to_goal_dist_start":0.1228,"object_z_max":0.037,"peak_contact_force":13.52493,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2010.0,"raw_peak_contact_force":43.68643,"subtask_id":"push_goal","tcp_end":[0.48966,-0.05704,0.0293],"tcp_start":[0.48971,-0.05705,0.02936],"tcp_to_object_dist_end":0.03099,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.50272,-0.07901,0.03379],"object_pos_start":[0.50735,-0.08158,0.03631],"object_to_goal_dist_end":0.00685,"object_to_goal_dist_start":0.00838,"object_z_max":0.03722,"peak_contact_force":0.54961,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1351.0,"raw_peak_contact_force":140.58548,"tcp_end":[0.48638,-0.0567,0.11991],"tcp_start":[0.48966,-0.05704,0.0293],"tcp_to_object_dist_end":0.09045,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13964,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.08524,"approach_behind.lateral_offset_x":0.00292,"contact_peg.contact_force_threshold":6.47314,"contact_peg.contact_speed":0.02129,"push_channel.max_push_force":44.65498,"push_channel.push_offset_x":0.00195,"push_channel.push_speed":0.04213,"retract.retract_speed":0.06078},"optimized_scores":{"best_composite_score":0.22203,"best_fitness_score":0.71203,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":191.0,"contact_point_centroid":[0.47498,-0.02949,0.04595],"force_p95":216.23606,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":243.91759,"mean_force":120.62153,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48676,-0.02951,0.04376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1337.0,"contact_point_centroid":[0.50404,0.11136,0.00936],"force_p95":59.17568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.58886,"mean_force":5.2596,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50349,0.16348,0.15873]},{"body_a":"attachment","body_b":"peg","contact_count":114.0,"contact_point_centroid":[0.51158,0.12689,0.05398],"force_p95":107.17313,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.82533,"mean_force":55.34164,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50811,0.13753,0.05344]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.5281,0.10632,0.06],"force_p95":41.63716,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.78929,"mean_force":33.76961,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49192,0.09788,0.02569]},{"body_a":"attachment","body_b":"peg","contact_count":949.0,"contact_point_centroid":[0.49879,0.02961,0.04434],"force_p95":15.65457,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.1153,"mean_force":10.46159,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49001,0.03982,0.02671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":889.0,"contact_point_centroid":[0.50762,0.00029,0.00995],"force_p95":14.0719,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.0467,"mean_force":10.26484,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49007,0.04143,0.02669]},{"body_a":"peg","body_b":"link7","contact_count":834.0,"contact_point_centroid":[0.52073,0.02502,0.06219],"force_p95":9.64668,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.80781,"mean_force":6.04808,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48997,0.04081,0.02663]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":777.0,"contact_point_centroid":[0.52509,0.00282,0.05027],"force_p95":10.70946,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.76647,"mean_force":7.49186,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48964,0.02909,0.02688]},{"body_a":"attachment","body_b":"peg","contact_count":161.0,"contact_point_centroid":[0.49663,-0.0391,0.06161],"force_p95":8.12266,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.49586,"mean_force":1.55545,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48667,-0.02951,0.04618]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":123.0,"contact_point_centroid":[0.52505,-0.05371,0.05179],"force_p95":9.58014,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.43692,"mean_force":2.02352,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48683,-0.02965,0.04087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":768.0,"contact_point_centroid":[0.50744,-0.0558,0.00961],"force_p95":0.65151,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.21881,"mean_force":0.56532,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4853,-0.02968,0.07483]},{"body_a":"peg","body_b":"channel_base_body","contact_count":962.0,"contact_point_centroid":[0.50066,0.0924,0.00963],"force_p95":2.30825,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.53333,"mean_force":1.13768,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49445,0.13504,0.02802]},{"body_a":"attachment","body_b":"peg","contact_count":441.0,"contact_point_centroid":[0.49891,0.11334,0.03998],"force_p95":2.65445,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.19697,"mean_force":1.49632,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49492,0.12504,0.02825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50048,0.10265,0.00943],"force_p95":0.63662,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30415,"mean_force":0.554,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.50095,0.14365,0.03222]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50384,0.12099,0.03463],"force_p95":1.01835,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.04942,"mean_force":0.57561,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.50584,0.13278,0.03437]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49974,0.19943,0.29917]}],"total_contact_groups":16},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50548,-0.04931,0.03388],"final_tcp_position":[0.48466,-0.02979,0.11868],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":243.91759,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1367.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11175,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.2968,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1467.0,"raw_peak_contact_force":110.58886,"subtask_id":"pre_push","tcp_end":[0.50784,0.133,0.03683],"tcp_start":[0.50642,0.14663,0.09563],"tcp_to_object_dist_end":0.02186,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50032,0.10343,0.03394],"object_pos_start":[0.49912,0.1042,0.03559],"object_to_goal_dist_end":0.18353,"object_to_goal_dist_start":0.18426,"object_z_max":0.0356,"peak_contact_force":0.54706,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":557.0,"raw_peak_contact_force":1.30415,"tcp_end":[0.49684,0.15635,0.0318],"tcp_start":[0.50784,0.133,0.03683],"tcp_to_object_dist_end":0.05307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50381,0.08788,0.03537],"object_pos_start":[0.50032,0.10343,0.03394],"object_to_goal_dist_end":0.16798,"object_to_goal_dist_start":0.18353,"object_z_max":0.03555,"peak_contact_force":2.08692,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1403.0,"raw_peak_contact_force":4.53333,"tcp_end":[0.49545,0.11691,0.02861],"tcp_start":[0.49684,0.15635,0.0318],"tcp_to_object_dist_end":0.03097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50754,-0.05378,0.03659],"object_pos_start":[0.50381,0.08788,0.03537],"object_to_goal_dist_end":0.0275,"object_to_goal_dist_start":0.16798,"object_z_max":0.03704,"peak_contact_force":7.85496,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3468.0,"raw_peak_contact_force":43.78929,"subtask_id":"push_goal","tcp_end":[0.48791,-0.02996,0.02807],"tcp_start":[0.49545,0.11691,0.02861],"tcp_to_object_dist_end":0.03202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.50548,-0.04931,0.03388],"object_pos_start":[0.50754,-0.05378,0.03659],"object_to_goal_dist_end":0.03177,"object_to_goal_dist_start":0.0275,"object_z_max":0.03685,"peak_contact_force":0.54921,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1243.0,"raw_peak_contact_force":243.91759,"tcp_end":[0.48466,-0.02979,0.11868],"tcp_start":[0.48791,-0.02996,0.02807],"tcp_to_object_dist_end":0.08947,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.05176,"approach_behind.lateral_offset_x":-0.00572,"contact_peg.contact_force_threshold":8.50802,"contact_peg.contact_speed":0.01264,"push_channel.max_push_force":35.06498,"push_channel.push_offset_x":-0.00337,"push_channel.push_speed":0.02485,"retract.retract_speed":0.04941},"optimized_scores":{"best_composite_score":-0.13654,"best_fitness_score":0.15346,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":911.0,"contact_point_centroid":[0.47474,0.1678,-0.00196],"force_p95":0.72712,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.28455,"mean_force":0.82151,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47677,0.16844,0.07672]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.49032,0.16495,0.03049],"force_p95":23.01197,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.82756,"mean_force":12.04417,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47934,0.1695,0.03207]},{"body_a":"peg","body_b":"world","contact_count":4.0,"contact_point_centroid":[0.4999,0.15377,-0.00274],"force_p95":51.37139,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.45485,"mean_force":50.96638,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4801,0.16943,0.03165]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49111,0.16494,0.03028],"force_p95":50.8938,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.97956,"mean_force":50.47582,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4801,0.16943,0.03165]},{"body_a":"peg","body_b":"world","contact_count":2.0,"contact_point_centroid":[0.48295,0.17187,-0.00264],"force_p95":47.72946,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.07767,"mean_force":26.59554,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48017,0.16936,0.03173]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49117,0.16484,0.03041],"force_p95":47.29481,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.60788,"mean_force":26.47722,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48017,0.16936,0.03173]},{"body_a":"peg","body_b":"world","contact_count":426.0,"contact_point_centroid":[0.4971,0.15441,-0.00273],"force_p95":45.38365,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.45219,"mean_force":32.34341,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.48386,0.15888,0.03188]},{"body_a":"attachment","body_b":"peg","contact_count":420.0,"contact_point_centroid":[0.49543,0.15762,0.03033],"force_p95":44.88182,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.96003,"mean_force":32.32955,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.48377,0.15909,0.03185]},{"body_a":"peg","body_b":"world","contact_count":397.0,"contact_point_centroid":[0.49665,0.15785,-0.0018],"force_p95":0.80195,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.99488,"mean_force":0.61662,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48552,0.14824,0.06358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1012.0,"contact_point_centroid":[0.49609,0.1193,0.00942],"force_p95":0.61676,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54399,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48968,0.17511,0.19393]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49948,0.19931,0.29847]}],"total_contact_groups":11},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.46743,0.16338,0.01414],"final_tcp_position":[0.47689,0.16847,0.12216],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":52.28455,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1437.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.12465,0.0334],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.2048,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53281,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1433.0,"raw_peak_contact_force":2.99488,"subtask_id":"pre_push","tcp_end":[0.49038,0.14429,0.03424],"tcp_start":[0.4823,0.15391,0.10357],"tcp_to_object_dist_end":0.02044,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.48297,0.17185,0.01282],"object_pos_start":[0.49953,0.16014,0.01412],"object_to_goal_dist_end":0.25389,"object_to_goal_dist_start":0.24153,"object_z_max":0.01413,"peak_contact_force":47.45219,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":846.0,"raw_peak_contact_force":47.45219,"tcp_end":[0.48018,0.16935,0.03173],"tcp_start":[0.49038,0.14429,0.03424],"tcp_to_object_dist_end":0.01928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":960.0,"object_pos_end":[0.48292,0.17188,0.01274],"object_pos_start":[0.48297,0.17185,0.01282],"object_to_goal_dist_end":0.25393,"object_to_goal_dist_start":0.25389,"object_z_max":0.01282,"peak_contact_force":50.07767,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":50.07767,"tcp_end":[0.48014,0.16938,0.03169],"tcp_start":[0.48018,0.16935,0.03173],"tcp_to_object_dist_end":0.01932,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.4829,0.1719,0.0127],"object_pos_start":[0.48292,0.17188,0.01274],"object_to_goal_dist_end":0.25396,"object_to_goal_dist_start":0.25393,"object_z_max":0.01274,"peak_contact_force":51.45485,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":51.45485,"subtask_id":"push_goal","tcp_end":[0.48001,0.16952,0.03158],"tcp_start":[0.48005,0.16948,0.03161],"tcp_to_object_dist_end":0.01925,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.46743,0.16338,0.01414],"object_pos_start":[0.48281,0.17198,0.0126],"object_to_goal_dist_end":0.24691,"object_to_goal_dist_start":0.25405,"object_z_max":0.01449,"peak_contact_force":0.60889,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":928.0,"raw_peak_contact_force":52.28455,"tcp_end":[0.47689,0.16847,0.12216],"tcp_start":[0.48001,0.16952,0.03158],"tcp_to_object_dist_end":0.10856,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```