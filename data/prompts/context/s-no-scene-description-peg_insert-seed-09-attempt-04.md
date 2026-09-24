## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.3951 | 0.86 | ❌ rejected |
| 3 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3393 | 0.74 | ❌ rejected |
| 2 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5025 | 0.91 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | 0.4018 | 0.77 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | 0.4018 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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

## Current Skill (Q=0.395) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_hole
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: insert_peg
  weight: 0.7
phases:
- id: approach_hole
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_hole
- id: align_hole
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_hole
- id: descend_insert
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insert_depth:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insert_peg
- id: release_peg
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_hole** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_hole** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_insert** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.08, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **release_peg** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.395
- **task_score** (E): 0.863
- **fitness_score**: 0.568  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.267
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole_high | 1.00 | 0.00 | 0.1746 |
| align_hole_xy | 0.67 | 0.33 | 0.0439 |
| contact_touch | 0.33 | 0.33 | 0.0003 |
| descend_insert | 1.00 | 1.00 | 0.0493 |
| release_peg | 1.00 | 1.00 | 0.0005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole_high | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, -0.012, 0.129) | (0.504, -0.000, 0.340)→(0.519, -0.012, 0.167) | 0.260→0.093 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole_xy | align | 0.67 / step_budget | (0.508, -0.012, 0.129)→(0.529, -0.012, 0.090) | (0.519, -0.012, 0.167)→(0.548, -0.012, 0.121) | 0.093→0.093 | 0.33 / 0.333 | 84.227 | 634.296 |
| contact_touch | contact | 0.33 / guard_failure | (0.529, -0.012, 0.090)→(0.529, -0.012, 0.090) | (0.548, -0.012, 0.121)→(0.548, -0.012, 0.121) | 0.093→0.093 | 0.33 / 0.333 | 35.634 | 35.634 |
| descend_insert | descend | 1.00 / force_exceeded | (0.529, -0.012, 0.090)→(0.528, -0.012, 0.041) | (0.548, -0.012, 0.121)→(0.547, -0.012, 0.072) | 0.093→0.057 | 1.00 / 1.000 | 97.210 | 52.893 |
| release_peg | release | 1.00 / step_budget | (0.528, -0.012, 0.041)→(0.528, -0.012, 0.040) | (0.547, -0.012, 0.072)→(0.547, -0.012, 0.071) | 0.057→0.057 | 1.00 / 1.333 | 64.709 | 86.013 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.857
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.857
- phase_score: 0.197
- phase_breakdown.reach_above_hole_score: 0.131
- phase_breakdown.insert_peg_score: 0.226

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.648
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.885
- **Median Q (composite search score)**: 0.408
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.351


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ad55441961509110caa3e00662ff00c043a366a9841ef346adcb2ae98eb0fa2d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `848090e975b2909410760ed4539d133eb61635ea5a8640e3622d2871416125a9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.18018,"average_mean_iterations":38.81081,"average_solve_count":111.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole_xy.align_speed":0.19937,"approach_hole_high.approach_speed":0.09349,"contact_touch.contact_force_limit":5.20383,"contact_touch.contact_speed":0.02644,"descend_insert.insert_depth":0.14998,"descend_insert.insert_force_threshold":24.0048,"descend_insert.insert_speed":0.01647},"optimized_scores":{"best_composite_score":0.40786,"best_fitness_score":0.64786,"best_task_score":0.88494},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.53547,-0.01563,0.04996],"force_p95":79.01301,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.67997,"mean_force":73.41935,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.52099,-0.01568,0.05383]}],"total_contact_groups":1},"final_pose_error":0.1242,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52087,-0.01566,0.0539],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":79.67997,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.5328,-0.0149,0.16719],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09434,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52288,-0.01492,0.12844],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.5328,-0.0149,0.16719],"object_pos_start":[0.5328,-0.0149,0.16719],"object_to_goal_dist_end":0.09434,"object_to_goal_dist_start":0.09434,"peak_contact_force":0.0,"phase_name":"align_hole_xy","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52288,-0.01492,0.12844],"tcp_start":[0.52288,-0.01492,0.12844],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53271,-0.01493,0.16671],"object_pos_start":[0.5328,-0.0149,0.16719],"object_to_goal_dist_end":0.09387,"object_to_goal_dist_start":0.09434,"object_z_max":0.16719,"peak_contact_force":0.0,"phase_name":"contact_touch","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.52276,-0.01495,0.12797],"tcp_start":[0.52288,-0.01492,0.12844],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.53131,-0.01564,0.09251],"object_pos_start":[0.53271,-0.01493,0.16671],"object_to_goal_dist_end":0.03717,"object_to_goal_dist_start":0.09387,"object_z_max":0.16671,"peak_contact_force":65.69982,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.52087,-0.01566,0.0539],"tcp_start":[0.52276,-0.01495,0.12797],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5315,-0.01567,0.0925],"object_pos_start":[0.53131,-0.01564,0.09251],"object_to_goal_dist_end":0.03734,"object_to_goal_dist_start":0.03717,"object_z_max":0.09251,"peak_contact_force":72.70984,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":79.67997,"tcp_end":[0.52107,-0.01569,0.05388],"tcp_start":[0.52087,-0.01566,0.0539],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.10638,"average_mean_iterations":23.91489,"average_solve_count":188.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole_xy.align_speed":0.04341,"approach_hole_high.approach_speed":0.02222,"contact_touch.contact_force_limit":6.05746,"contact_touch.contact_speed":0.01425,"descend_insert.insert_depth":0.14998,"descend_insert.insert_force_threshold":31.26639,"descend_insert.insert_speed":0.02466},"optimized_scores":{"best_composite_score":0.35619,"best_fitness_score":0.59619,"best_task_score":0.84689},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.54189,-0.0214,0.04996],"force_p95":77.93317,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.64603,"mean_force":72.89729,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.52736,-0.02148,0.05364]}],"total_contact_groups":1},"final_pose_error":0.12406,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.52718,-0.02146,0.05371],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":79.64603,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.53835,-0.02045,0.1667],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09699,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52892,-0.0205,0.12783],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.53835,-0.02045,0.1667],"object_pos_start":[0.53835,-0.02045,0.1667],"object_to_goal_dist_end":0.09699,"object_to_goal_dist_start":0.09699,"peak_contact_force":0.0,"phase_name":"align_hole_xy","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52892,-0.0205,0.12783],"tcp_start":[0.52892,-0.0205,0.12783],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53827,-0.02049,0.16624],"object_pos_start":[0.53835,-0.02045,0.1667],"object_to_goal_dist_end":0.09655,"object_to_goal_dist_start":0.09699,"object_z_max":0.1667,"peak_contact_force":0.0,"phase_name":"contact_touch","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.52882,-0.02054,0.12738],"tcp_start":[0.52892,-0.0205,0.12783],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.53712,-0.02142,0.09246],"object_pos_start":[0.53827,-0.02049,0.16624],"object_to_goal_dist_end":0.04463,"object_to_goal_dist_start":0.09655,"object_z_max":0.16624,"peak_contact_force":67.25064,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.52718,-0.02146,0.05371],"tcp_start":[0.52882,-0.02054,0.12738],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53738,-0.02144,0.09244],"object_pos_start":[0.53712,-0.02142,0.09246],"object_to_goal_dist_end":0.04485,"object_to_goal_dist_start":0.04463,"object_z_max":0.09246,"peak_contact_force":72.59312,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":79.64603,"tcp_end":[0.52745,-0.02149,0.05369],"tcp_start":[0.52718,-0.02146,0.05371],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.93617,"average_solve_count":47.0,"average_success_count":47.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole_xy.align_speed":0.14644,"approach_hole_high.approach_speed":0.17622,"contact_touch.contact_force_limit":7.34383,"contact_touch.contact_speed":0.02544,"descend_insert.insert_depth":0.02833,"descend_insert.insert_force_threshold":32.47162,"descend_insert.insert_speed":0.03775},"optimized_scores":{"best_composite_score":0.42126,"best_fitness_score":0.46126,"best_task_score":0.857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.63224,-0.00338,-0.0002],"force_p95":1870.74338,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1902.88925,"mean_force":999.85793,"phase_index":1.0,"phase_name":"align_hole_xy","phase_type":"align","tcp_position_centroid":[0.53309,-0.00028,0.01553]},{"body_a":"attachment","body_b":"peg_socket","contact_count":188.0,"contact_point_centroid":[0.5297,-5e-05,0.02944],"force_p95":1035.5439,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1480.6878,"mean_force":360.12386,"phase_index":1.0,"phase_name":"align_hole_xy","phase_type":"align","tcp_position_centroid":[0.53424,-0.00019,0.01539]},{"body_a":"attachment","body_b":"world","contact_count":36.0,"contact_point_centroid":[0.55212,2e-05,-0.00409],"force_p95":1190.80668,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1359.62934,"mean_force":399.62008,"phase_index":1.0,"phase_name":"align_hole_xy","phase_type":"align","tcp_position_centroid":[0.54326,-0.0,0.0038]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.5301,9e-05,0.02858],"force_p95":151.86219,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.67809,"mean_force":90.51912,"phase_index":3.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.53554,-8e-05,0.01468]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.53009,0.00011,0.0286],"force_p95":101.55707,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.90217,"mean_force":53.45109,"phase_index":2.0,"phase_name":"contact_touch","phase_type":"contact","tcp_position_centroid":[0.53554,-8e-05,0.0147]},{"body_a":"attachment","body_b":"peg_socket","contact_count":198.0,"contact_point_centroid":[0.53025,4e-05,0.02798],"force_p95":93.84472,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.71419,"mean_force":61.45338,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.53586,-0.00011,0.01408]},{"body_a":"attachment","body_b":"world","contact_count":101.0,"contact_point_centroid":[0.54156,-0.0001,-3e-05],"force_p95":91.42796,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.57275,"mean_force":64.33284,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.5359,-0.00012,0.01384]}],"total_contact_groups":7},"final_pose_error":0.07501,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.53555,-8e-05,0.01469],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":1902.88925,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":307.0,"n_steps_budget":690.0,"object_pos_end":[0.48532,-0.0001,0.16695],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08818,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47119,-0.0001,0.12953],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.57262,0.0001,0.02972],"object_pos_start":[0.48532,-0.0001,0.16695],"object_to_goal_dist_end":0.08833,"object_to_goal_dist_start":0.08818,"object_z_max":0.16695,"peak_contact_force":252.68165,"phase_name":"align_hole_xy","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":247.0,"raw_peak_contact_force":1902.88925,"subtask_id":"reach_above_hole","tcp_end":[0.53555,-8e-05,0.0147],"tcp_start":[0.47119,-0.0001,0.12953],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.57262,0.0001,0.02971],"object_pos_start":[0.57262,0.0001,0.02972],"object_to_goal_dist_end":0.08833,"object_to_goal_dist_start":0.08833,"object_z_max":0.02973,"peak_contact_force":106.90217,"phase_name":"contact_touch","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":106.90217,"subtask_id":"insert_peg","tcp_end":[0.53555,-8e-05,0.01468],"tcp_start":[0.53555,-8e-05,0.0147],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.57261,0.0001,0.02972],"object_pos_start":[0.57262,0.0001,0.02971],"object_to_goal_dist_end":0.08833,"object_to_goal_dist_start":0.08833,"object_z_max":0.02971,"peak_contact_force":158.67809,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":158.67809,"subtask_id":"insert_peg","tcp_end":[0.53555,-8e-05,0.01469],"tcp_start":[0.53555,-8e-05,0.01468],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57297,8e-05,0.02893],"object_pos_start":[0.57261,0.0001,0.02972],"object_to_goal_dist_end":0.08907,"object_to_goal_dist_start":0.08833,"object_z_max":0.02972,"peak_contact_force":48.8246,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":299.0,"raw_peak_contact_force":98.71419,"tcp_end":[0.53592,-0.00012,0.01386],"tcp_start":[0.53555,-8e-05,0.01469],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```