## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3411 | 0.65 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1002 | 0.12 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3662 | 0.39 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3571 | 0.68 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0108 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.65 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.341) — your mutation base

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

- **Composite score**: 0.341
- **task_score** (E): 0.655
- **fitness_score**: 0.590  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 0.00 | 1.00 | 0.0740 |
| contact_peg | 0.33 | 1.00 | 0.0219 |
| push_channel | 0.00 | 1.00 | 0.0910 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 0.00 / step_budget | (0.496, 0.141, 0.106)→(0.503, 0.121, 0.035) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.333 | 10.023 | 70.426 |
| contact_peg | contact | 0.33 / step_budget | (0.503, 0.121, 0.035)→(0.499, 0.100, 0.032) | (0.502, 0.106, 0.029)→(0.499, 0.087, 0.028) | 0.186→0.167 | 1.00 / 2.000 | 13.888 | 15.387 |
| push_channel | push | 0.00 / guard_failure | (0.499, 0.100, 0.032)→(0.497, 0.009, 0.033) | (0.499, 0.087, 0.028)→(0.501, -0.003, 0.029) | 0.167→0.086 | 1.00 / 2.667 | 28.530 | 42.870 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.697
- phase_breakdown.pre_push_score: 0.925
- phase_breakdown.push_goal_score: 0.600

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.818
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.444
- **K-run variance**: 0.0242
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22024,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07126,"approach_behind.lateral_offset_x":0.00122,"contact_peg.contact_force_threshold":12.05418,"contact_peg.contact_speed":0.01976,"push_channel.push_speed":0.04665,"retract.retract_speed":0.07304},"optimized_scores":{"best_composite_score":0.44369,"best_fitness_score":0.80369,"best_task_score":0.96456},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":61.0,"contact_point_centroid":[0.49837,-0.10123,0.03801],"force_p95":34.26129,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.48383,"mean_force":23.45828,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49831,-0.05493,0.03038]},{"body_a":"attachment","body_b":"peg","contact_count":626.0,"contact_point_centroid":[0.49688,-0.0144,0.03057],"force_p95":25.16567,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.28527,"mean_force":2.90659,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49698,-0.00249,0.02823]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1473.0,"contact_point_centroid":[0.50324,0.06598,0.0094],"force_p95":0.80129,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.92919,"mean_force":0.81537,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49953,0.14079,0.15919]},{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.50355,0.08153,0.04504],"force_p95":11.14198,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.73366,"mean_force":6.05918,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50369,0.09349,0.04473]},{"body_a":"peg","body_b":"channel_base_body","contact_count":567.0,"contact_point_centroid":[0.49554,-0.03482,0.00992],"force_p95":2.00837,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.98586,"mean_force":1.08044,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49689,0.00268,0.02807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":755.0,"contact_point_centroid":[0.49597,0.03598,0.0098],"force_p95":1.11788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05477,"mean_force":0.70495,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49993,0.07317,0.02997]},{"body_a":"attachment","body_b":"peg","contact_count":626.0,"contact_point_centroid":[0.49865,0.06082,0.03007],"force_p95":0.80115,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.81419,"mean_force":0.42593,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49984,0.07274,0.0299]}],"total_contact_groups":7},"final_pose_error":0.06215,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49839,-0.08687,0.03533],"final_tcp_position":[0.49846,-0.0576,0.03048],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":44.48383,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1494.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.59907,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1540.0,"raw_peak_contact_force":14.92919,"subtask_id":"pre_push","tcp_end":[0.50474,0.08924,0.03463],"tcp_start":[0.49964,0.12028,0.11305],"tcp_to_object_dist_end":0.02189,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":755.0,"n_steps_budget":960.0,"object_pos_end":[0.49676,0.03077,0.0347],"object_pos_start":[0.50264,0.05901,0.0342],"object_to_goal_dist_end":0.11094,"object_to_goal_dist_start":0.13916,"object_z_max":0.03478,"peak_contact_force":0.49582,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1381.0,"raw_peak_contact_force":2.05477,"tcp_end":[0.49881,0.06069,0.02954],"tcp_start":[0.50474,0.08924,0.03463],"tcp_to_object_dist_end":0.03043,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.49839,-0.08687,0.03533],"object_pos_start":[0.49676,0.03077,0.0347],"object_to_goal_dist_end":0.00846,"object_to_goal_dist_start":0.11094,"object_z_max":0.03548,"peak_contact_force":1.46329,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1254.0,"raw_peak_contact_force":44.48383,"subtask_id":"push_goal","tcp_end":[0.49846,-0.0576,0.03048],"tcp_start":[0.49881,0.06069,0.02954],"tcp_to_object_dist_end":0.02966,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97521,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.0393,"approach_behind.lateral_offset_x":0.00073,"contact_peg.contact_force_threshold":16.92843,"contact_peg.contact_speed":0.02489,"push_channel.push_speed":0.03224,"retract.retract_speed":0.06516},"optimized_scores":{"best_composite_score":0.45829,"best_fitness_score":0.81829,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":185.0,"contact_point_centroid":[0.51485,0.12899,0.05458],"force_p95":160.97548,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":167.31394,"mean_force":104.44977,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50914,0.13894,0.05335]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1487.0,"contact_point_centroid":[0.50515,0.11207,0.00928],"force_p95":115.26371,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":163.89731,"mean_force":13.51438,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50272,0.16353,0.15773]},{"body_a":"attachment","body_b":"peg","contact_count":780.0,"contact_point_centroid":[0.50195,0.00282,0.04285],"force_p95":11.66971,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.63058,"mean_force":4.04515,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49747,0.0144,0.03258]},{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.50718,-0.10042,0.06031],"force_p95":37.70979,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.35685,"mean_force":29.08014,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49672,-0.05421,0.03457]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":45.0,"contact_point_centroid":[0.52547,0.11141,0.04673],"force_p95":6.09495,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.17708,"mean_force":2.42975,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50791,0.16052,0.13744]},{"body_a":"peg","body_b":"channel_base_body","contact_count":509.0,"contact_point_centroid":[0.50482,-0.0187,0.00992],"force_p95":7.65495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.44593,"mean_force":3.74102,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49767,0.02546,0.03234]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":543.0,"contact_point_centroid":[0.52507,-0.02444,0.02714],"force_p95":4.1673,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.98631,"mean_force":1.25977,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49723,0.00356,0.03276]},{"body_a":"peg","body_b":"channel_base_body","contact_count":697.0,"contact_point_centroid":[0.50215,0.07152,0.00994],"force_p95":2.03693,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.63722,"mean_force":1.14568,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5031,0.1144,0.03373]},{"body_a":"attachment","body_b":"peg","contact_count":641.0,"contact_point_centroid":[0.50313,0.10197,0.03708],"force_p95":1.67247,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.026,"mean_force":0.86916,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50299,0.11395,0.03364]}],"total_contact_groups":9},"final_pose_error":0.02633,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50717,-0.08252,0.03588],"final_tcp_position":[0.49658,-0.05526,0.03446],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":167.31394,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1509.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11176,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.43587,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1717.0,"raw_peak_contact_force":167.31394,"subtask_id":"pre_push","tcp_end":[0.50832,0.13442,0.03769],"tcp_start":[0.50412,0.1515,0.11427],"tcp_to_object_dist_end":0.02345,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":767.0,"n_steps_budget":930.0,"object_pos_end":[0.50101,0.0693,0.03494],"object_pos_start":[0.50549,0.09773,0.03899],"object_to_goal_dist_end":0.14939,"object_to_goal_dist_start":0.17782,"object_z_max":0.03919,"peak_contact_force":0.70183,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1338.0,"raw_peak_contact_force":3.63722,"tcp_end":[0.50173,0.09923,0.03409],"tcp_start":[0.50832,0.13442,0.03769],"tcp_to_object_dist_end":0.02995,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":974.0,"n_steps_budget":1000.0,"object_pos_end":[0.50717,-0.08252,0.03588],"object_pos_start":[0.50101,0.0693,0.03494],"object_to_goal_dist_end":0.00864,"object_to_goal_dist_start":0.14939,"object_z_max":0.03621,"peak_contact_force":43.63058,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1874.0,"raw_peak_contact_force":43.63058,"subtask_id":"push_goal","tcp_end":[0.49658,-0.05526,0.03446],"tcp_start":[0.50173,0.09923,0.03409],"tcp_to_object_dist_end":0.02928,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66292,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07281,"approach_behind.lateral_offset_x":-0.00104,"contact_peg.contact_force_threshold":14.32015,"contact_peg.contact_speed":0.01261,"push_channel.push_speed":0.04051,"retract.retract_speed":0.07195},"optimized_scores":{"best_composite_score":0.12125,"best_fitness_score":0.14792,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":5.0,"contact_point_centroid":[0.49927,0.13526,-0.00189],"force_p95":40.34253,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.49624,"mean_force":36.4993,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49516,0.13956,0.03265]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.49937,0.13524,-0.00199],"force_p95":40.46774,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.46774,"mean_force":40.46774,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49518,0.1396,0.03273]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50196,0.13511,0.03178],"force_p95":39.72819,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.72819,"mean_force":39.72819,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49518,0.1396,0.03273]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.5017,0.14058,0.03188],"force_p95":39.59129,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.71414,"mean_force":35.93644,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49516,0.13956,0.03265]},{"body_a":"peg","body_b":"world","contact_count":374.0,"contact_point_centroid":[0.49623,0.15743,-0.0018],"force_p95":0.91508,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.03436,"mean_force":0.8403,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49122,0.14246,0.04763]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50193,0.1352,0.03185],"force_p95":28.06728,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.28397,"mean_force":16.52045,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49509,0.13962,0.03286]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1118.0,"contact_point_centroid":[0.49608,0.11922,0.00945],"force_p95":0.60622,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54174,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4905,0.17094,0.17591]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49953,0.19931,0.29842]}],"total_contact_groups":8},"final_pose_error":0.17987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49859,0.1601,0.01466],"final_tcp_position":[0.49508,0.13944,0.03257],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":40.49624,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1520.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.12,0.03407],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.20012,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":29.03436,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1521.0,"raw_peak_contact_force":29.03436,"subtask_id":"pre_push","tcp_end":[0.49518,0.1396,0.03273],"tcp_start":[0.48477,0.15062,0.08958],"tcp_to_object_dist_end":0.01966,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49859,0.16011,0.01425],"object_pos_start":[0.49859,0.16012,0.01417],"object_to_goal_dist_end":0.24149,"object_to_goal_dist_start":0.24151,"object_z_max":0.01417,"peak_contact_force":40.46774,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":40.46774,"tcp_end":[0.49519,0.13959,0.03271],"tcp_start":[0.49518,0.1396,0.03273],"tcp_to_object_dist_end":0.02781,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.49859,0.1601,0.01466],"object_pos_start":[0.49859,0.16011,0.01425],"object_to_goal_dist_end":0.24143,"object_to_goal_dist_start":0.24149,"object_z_max":0.01455,"peak_contact_force":40.49624,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":40.49624,"subtask_id":"push_goal","tcp_end":[0.49508,0.13944,0.03257],"tcp_start":[0.49519,0.13959,0.03271],"tcp_to_object_dist_end":0.02756,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```