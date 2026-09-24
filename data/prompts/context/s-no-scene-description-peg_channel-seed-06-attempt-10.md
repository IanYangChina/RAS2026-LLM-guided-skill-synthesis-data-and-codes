## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3597 | 0.68 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3139 | 0.77 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3307 | 0.46 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3411 | 0.65 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1002 | 0.12 | ❌ rejected |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.360) — your mutation base

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

- **Composite score**: 0.360
- **task_score** (E): 0.683
- **fitness_score**: 0.609  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 0.33 | 1.00 | 0.0656 |
| contact_peg | 0.33 | 1.00 | 0.0276 |
| push_channel | 0.00 | 1.00 | 0.0999 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 0.33 / step_budget | (0.494, 0.139, 0.098)→(0.499, 0.121, 0.035) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.667 | 1.197 | 57.270 |
| contact_peg | contact | 0.33 / step_budget | (0.499, 0.121, 0.035)→(0.497, 0.094, 0.031) | (0.502, 0.090, 0.036)→(0.502, 0.066, 0.035) | 0.170→0.146 | 1.00 / 2.000 | 1288.400 | 4.698 |
| push_channel | push | 0.00 / guard_failure | (0.497, 0.094, 0.031)→(0.494, -0.006, 0.031) | (0.502, 0.066, 0.035)→(0.504, -0.032, 0.036) | 0.146→0.057 | 1.00 / 3.000 | 2088.209 | 41.736 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.698
- phase_breakdown.pre_push_score: 0.929
- phase_breakdown.push_goal_score: 0.599

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.819
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.435
- **K-run variance**: 0.0153
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15642,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.08277,"approach_behind.lateral_offset_x":0.00035,"contact_peg.contact_force_threshold":11.10379,"contact_peg.contact_speed":0.01866,"push_channel.push_speed":0.03629,"retract.retract_speed":0.0512},"optimized_scores":{"best_composite_score":0.4352,"best_fitness_score":0.7952,"best_task_score":0.94191},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":628.0,"contact_point_centroid":[0.49544,-0.01366,0.02957],"force_p95":24.05983,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.22212,"mean_force":2.93261,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49592,-0.00175,0.02836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.49747,-0.10135,0.03639],"force_p95":34.93756,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.97414,"mean_force":24.69167,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49731,-0.05527,0.03059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1455.0,"contact_point_centroid":[0.50314,0.06589,0.0094],"force_p95":0.73459,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.19135,"mean_force":0.82287,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49912,0.14045,0.15845]},{"body_a":"attachment","body_b":"peg","contact_count":75.0,"contact_point_centroid":[0.50314,0.08163,0.04741],"force_p95":10.98792,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.95565,"mean_force":5.49962,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50276,0.0936,0.04506]},{"body_a":"peg","body_b":"channel_base_body","contact_count":592.0,"contact_point_centroid":[0.49395,-0.03282,0.00991],"force_p95":2.04986,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.69812,"mean_force":1.1139,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49583,0.00319,0.0282]},{"body_a":"attachment","body_b":"peg","contact_count":641.0,"contact_point_centroid":[0.49821,0.06068,0.03011],"force_p95":0.80604,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.28739,"mean_force":0.42692,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49881,0.07265,0.02992]},{"body_a":"peg","body_b":"channel_base_body","contact_count":800.0,"contact_point_centroid":[0.49711,0.03654,0.00978],"force_p95":1.12673,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.07379,"mean_force":0.70299,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49891,0.07319,0.03]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":47.0,"contact_point_centroid":[0.47487,-0.03005,0.03027],"force_p95":0.89063,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07944,"mean_force":0.40723,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49562,-0.00016,0.02801]}],"total_contact_groups":8},"final_pose_error":0.06188,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49758,-0.08685,0.03507],"final_tcp_position":[0.49741,-0.05763,0.03064],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":40.22212,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1476.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":1.73768,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1530.0,"raw_peak_contact_force":14.19135,"subtask_id":"pre_push","tcp_end":[0.50387,0.08922,0.03463],"tcp_start":[0.49905,0.11871,0.10942],"tcp_to_object_dist_end":0.02183,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.49671,0.03096,0.03463],"object_pos_start":[0.50152,0.05943,0.03426],"object_to_goal_dist_end":0.11114,"object_to_goal_dist_start":0.13956,"object_z_max":0.03474,"peak_contact_force":0.68967,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1441.0,"raw_peak_contact_force":3.28739,"tcp_end":[0.49771,0.06095,0.02961],"tcp_start":[0.50387,0.08922,0.03463],"tcp_to_object_dist_end":0.03042,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":766.0,"n_steps_budget":1000.0,"object_pos_end":[0.49758,-0.08685,0.03507],"object_pos_start":[0.49671,0.03096,0.03463],"object_to_goal_dist_end":0.00878,"object_to_goal_dist_start":0.11114,"object_z_max":0.03532,"peak_contact_force":40.22212,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1324.0,"raw_peak_contact_force":40.22212,"subtask_id":"push_goal","tcp_end":[0.49741,-0.05763,0.03064],"tcp_start":[0.49771,0.06095,0.02961],"tcp_to_object_dist_end":0.02956,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20183,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07659,"approach_behind.lateral_offset_x":0.00153,"contact_peg.contact_force_threshold":17.50473,"contact_peg.contact_speed":0.02467,"push_channel.push_speed":0.02734,"retract.retract_speed":0.0729},"optimized_scores":{"best_composite_score":0.45858,"best_fitness_score":0.81858,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1416.0,"contact_point_centroid":[0.50525,0.11196,0.00928],"force_p95":110.28317,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.13935,"mean_force":12.6495,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50333,0.16251,0.15403]},{"body_a":"attachment","body_b":"peg","contact_count":180.0,"contact_point_centroid":[0.51474,0.12866,0.05502],"force_p95":142.03051,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":145.72184,"mean_force":95.26885,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50919,0.13875,0.05394]},{"body_a":"attachment","body_b":"peg","contact_count":802.0,"contact_point_centroid":[0.50236,0.00327,0.04277],"force_p95":11.72205,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.48039,"mean_force":4.20828,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49793,0.01489,0.03246]},{"body_a":"peg","body_b":"channel_base_body","contact_count":43.0,"contact_point_centroid":[0.50701,-0.10044,0.0603],"force_p95":38.09467,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.55273,"mean_force":29.84832,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49754,-0.05407,0.03448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":523.0,"contact_point_centroid":[0.50505,-0.01864,0.00992],"force_p95":7.72604,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.75314,"mean_force":4.12376,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49809,0.02545,0.03226]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":518.0,"contact_point_centroid":[0.52506,-0.02166,0.02413],"force_p95":3.09114,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.86605,"mean_force":1.08176,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49777,0.00641,0.03258]},{"body_a":"peg","body_b":"channel_base_body","contact_count":695.0,"contact_point_centroid":[0.49983,0.07465,0.00992],"force_p95":1.38389,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.47273,"mean_force":0.82554,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.503,0.11485,0.03364]},{"body_a":"attachment","body_b":"peg","contact_count":625.0,"contact_point_centroid":[0.50216,0.10283,0.03368],"force_p95":1.0443,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.69931,"mean_force":0.5441,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50296,0.11477,0.0336]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":33.0,"contact_point_centroid":[0.52555,0.10698,0.04443],"force_p95":2.33391,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.61971,"mean_force":0.61151,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50558,0.16753,0.16901]}],"total_contact_groups":9},"final_pose_error":0.02531,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50671,-0.08273,0.03574],"final_tcp_position":[0.49744,-0.0551,0.03438],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":146.13935,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1438.0,"n_steps_budget":1000.0,"object_pos_end":[0.50364,0.11181,0.03385],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.4502,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1629.0,"raw_peak_contact_force":146.13935,"subtask_id":"pre_push","tcp_end":[0.50806,0.13393,0.03772],"tcp_start":[0.50529,0.14719,0.09777],"tcp_to_object_dist_end":0.02289,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":736.0,"n_steps_budget":900.0,"object_pos_end":[0.50031,0.0705,0.03489],"object_pos_start":[0.50558,0.09912,0.03886],"object_to_goal_dist_end":0.15058,"object_to_goal_dist_start":0.17921,"object_z_max":0.03886,"peak_contact_force":0.82625,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1320.0,"raw_peak_contact_force":4.47273,"tcp_end":[0.50179,0.10046,0.03395],"tcp_start":[0.50806,0.13393,0.03772],"tcp_to_object_dist_end":0.03002,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":986.0,"n_steps_budget":1000.0,"object_pos_end":[0.50671,-0.08273,0.03574],"object_pos_start":[0.50031,0.0705,0.03489],"object_to_goal_dist_end":0.0084,"object_to_goal_dist_start":0.15058,"object_z_max":0.03616,"peak_contact_force":43.48039,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1886.0,"raw_peak_contact_force":43.48039,"subtask_id":"push_goal","tcp_end":[0.49744,-0.0551,0.03438],"tcp_start":[0.50179,0.10046,0.03395],"tcp_to_object_dist_end":0.02918,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19231,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07656,"approach_behind.lateral_offset_x":-0.00985,"contact_peg.contact_force_threshold":11.2961,"contact_peg.contact_speed":0.01892,"push_channel.push_speed":0.02684,"retract.retract_speed":0.09426},"optimized_scores":{"best_composite_score":0.18543,"best_fitness_score":0.21209,"best_task_score":0.10638},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.09619,0.02938],"force_p95":41.00893,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.50566,"mean_force":35.77267,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48683,0.09619,0.02739]},{"body_a":"peg","body_b":"channel_base_body","contact_count":134.0,"contact_point_centroid":[0.50724,0.06839,0.00994],"force_p95":16.56696,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.95651,"mean_force":12.61331,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48797,0.10731,0.02785]},{"body_a":"attachment","body_b":"peg","contact_count":137.0,"contact_point_centroid":[0.49678,0.09794,0.03858],"force_p95":13.87641,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.78364,"mean_force":9.90005,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48798,0.1075,0.02785]},{"body_a":"peg","body_b":"link7","contact_count":94.0,"contact_point_centroid":[0.51992,0.08919,0.06298],"force_p95":12.89262,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.30361,"mean_force":11.21085,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48732,0.10338,0.0274]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":106.0,"contact_point_centroid":[0.5251,0.08588,0.04133],"force_p95":8.77987,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.08772,"mean_force":5.15696,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48854,0.11099,0.02821]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1390.0,"contact_point_centroid":[0.49767,0.11619,0.0095],"force_p95":3.24452,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.47804,"mean_force":0.78719,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4856,0.165,0.14986]},{"body_a":"attachment","body_b":"peg","contact_count":86.0,"contact_point_centroid":[0.49028,0.13084,0.05615],"force_p95":8.37822,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.33619,"mean_force":4.20081,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48326,0.14152,0.04577]},{"body_a":"peg","body_b":"channel_base_body","contact_count":514.0,"contact_point_centroid":[0.50846,0.08841,0.00997],"force_p95":3.36687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.33436,"mean_force":2.06134,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48746,0.12893,0.03029]},{"body_a":"attachment","body_b":"peg","contact_count":528.0,"contact_point_centroid":[0.49613,0.11819,0.04634],"force_p95":4.81959,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.02532,"mean_force":2.38015,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48758,0.12857,0.03025]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":215.0,"contact_point_centroid":[0.5251,0.09781,0.04898],"force_p95":3.95751,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.40998,"mean_force":2.61103,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48961,0.12393,0.03022]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49949,0.1993,0.29839]}],"total_contact_groups":11},"final_pose_error":0.15493,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50693,0.07288,0.0369],"final_tcp_position":[0.48684,0.09593,0.02741],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":6180.92447,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1426.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11902,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":1.40458,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1500.0,"raw_peak_contact_force":11.47804,"subtask_id":"pre_push","tcp_end":[0.48616,0.13906,0.03379],"tcp_start":[0.47761,0.14998,0.08686],"tcp_to_object_dist_end":0.02233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.50758,0.09513,0.03654],"object_pos_start":[0.5001,0.11223,0.03604],"object_to_goal_dist_end":0.17533,"object_to_goal_dist_start":0.19227,"object_z_max":0.03669,"peak_contact_force":3863.68546,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1257.0,"raw_peak_contact_force":6.33436,"tcp_end":[0.49117,0.12098,0.03047],"tcp_start":[0.48616,0.13906,0.03379],"tcp_to_object_dist_end":0.03121,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,0.07288,0.0369],"object_pos_start":[0.50758,0.09513,0.03654],"object_to_goal_dist_end":0.15307,"object_to_goal_dist_start":0.17533,"object_z_max":0.03704,"peak_contact_force":6180.92447,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":474.0,"raw_peak_contact_force":41.50566,"subtask_id":"push_goal","tcp_end":[0.48684,0.09593,0.02741],"tcp_start":[0.49117,0.12098,0.03047],"tcp_to_object_dist_end":0.03202,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```