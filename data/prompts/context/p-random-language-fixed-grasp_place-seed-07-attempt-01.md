## Search State

- **Seed**: 7
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.4756 | 0.15 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.476) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: -0.476
- **task_score** (E): 0.145
- **fitness_score**: 0.174  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1935 |
| descend_1 | 0.00 | 1.00 | 0.0257 |
| grasp_1 | 1.00 | 1.00 | 0.0008 |
| lift_1 | 0.33 | 1.00 | 0.1094 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.391, 0.003, 0.141) | (0.511, 0.022, 0.030)→(0.471, 0.024, 0.016) | 0.271→0.296 | 1.00 / 5.000 | 192.200 | 1630.966 |
| descend_1 | descend | 0.00 / step_budget | (0.391, 0.003, 0.141)→(0.415, 0.006, 0.135) | (0.471, 0.024, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 5.000 | 269.722 | 388.746 |
| grasp_1 | grasp | 1.00 / step_budget | (0.415, 0.006, 0.135)→(0.415, 0.006, 0.134) | (0.471, 0.024, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 9.333 | 67.397 | 86.193 |
| lift_1 | lift | 0.33 / step_budget | (0.415, 0.006, 0.134)→(0.466, 0.014, 0.226) | (0.471, 0.024, 0.016)→(0.471, 0.024, 0.016) | 0.296→0.296 | 1.00 / 8.000 | 0.123 | 327.202 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.207
- phase_score: 0.159
- phase_breakdown.approach_1_score: 0.035
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.descend_1_score: 0.071
- phase_breakdown.release_1_score: 0.000
- grasp_place_fitness: 0.204

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.204
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.207
- **Median Q (composite search score)**: -0.474
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.397


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31868,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1708,"approach_1.speed":0.01211,"descend_1.grasp_z_offset":0.01773,"descend_1.speed":0.01714,"lift_1.lift_height":0.24812,"lift_1.speed":0.05217,"retract_1.retract_height":0.23716,"retract_1.speed":0.07339,"transport_1.arc_height":0.09275,"transport_1.speed":0.02032},"optimized_scores":{"best_composite_score":-0.4457,"best_fitness_score":0.2043,"best_task_score":0.20654},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.63009,0.0047,-0.00047],"force_p95":194.71447,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1628.22204,"mean_force":200.54984,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3873,0.0043,0.12142]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.63871,0.00871,-0.0003],"force_p95":294.28059,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":377.71442,"mean_force":269.97597,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.40571,0.00932,0.1418]},{"body_a":"world","body_b":"link6","contact_count":14.0,"contact_point_centroid":[0.65307,0.01135,-9e-05],"force_p95":72.25592,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.00103,"mean_force":20.83081,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.41511,0.01202,0.13386]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.6529,0.01131,-0.00014],"force_p95":82.53031,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.91493,"mean_force":71.30787,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41493,0.01194,0.13375]},{"body_a":"grasp_target","body_b":"link7","contact_count":288.0,"contact_point_centroid":[0.49,0.0228,0.04202],"force_p95":1.49484,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.83935,"mean_force":0.53998,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38406,0.00307,0.10157]},{"body_a":"grasp_target","body_b":"hand","contact_count":253.0,"contact_point_centroid":[0.48379,0.02452,0.0544],"force_p95":1.86515,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.41174,"mean_force":0.49908,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38366,0.00302,0.09951]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.48221,0.04766,-0.00265],"force_p95":0.36814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.30918,"mean_force":0.18063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40215,0.00423,0.13436]},{"body_a":"grasp_target","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.52645,0.02179,-0.00201],"force_p95":0.55965,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56396,"mean_force":0.4284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37075,0.00254,0.055]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47163,0.04998,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.40571,0.00932,0.1418]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47163,0.04998,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41493,0.01194,0.13375]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47163,0.04998,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43138,0.02436,0.1717]},{"body_a":"left_finger","body_b":"right_finger","contact_count":333.0,"contact_point_centroid":[0.41705,0.0119,0.13264],"force_p95":0.01396,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01135,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41502,0.01191,0.13357]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4202.0,"contact_point_centroid":[0.43331,0.02433,0.17075],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.0106,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43136,0.02434,0.17164]},{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.52679,0.00771,-0.00273],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37187,0.00258,0.0534]}],"total_contact_groups":14},"final_pose_error":0.06096,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.47163,0.04998,0.01602],"final_tcp_position":[0.44845,0.03561,0.20963],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1628.22204,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47163,0.04998,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.23659,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":192.09902,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4828.0,"raw_peak_contact_force":1628.22204,"subtask_id":"approach_1","tcp_end":[0.39139,0.00638,0.14175],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15539,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47163,0.04998,0.01602],"object_pos_start":[0.47163,0.04998,0.01602],"object_to_goal_dist_end":0.23659,"object_to_goal_dist_start":0.23659,"object_z_max":0.01602,"peak_contact_force":265.52934,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":377.71442,"subtask_id":"descend_1","tcp_end":[0.41449,0.01197,0.13415],"tcp_start":[0.39139,0.00638,0.14175],"tcp_to_object_dist_end":0.13662,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47163,0.04998,0.01602],"object_pos_start":[0.47163,0.04998,0.01602],"object_to_goal_dist_end":0.23659,"object_to_goal_dist_start":0.23659,"object_z_max":0.01602,"peak_contact_force":67.3817,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2583.0,"raw_peak_contact_force":85.91493,"subtask_id":"grasp_1","tcp_end":[0.41502,0.01191,0.13356],"tcp_start":[0.41449,0.01197,0.13415],"tcp_to_object_dist_end":0.1359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47163,0.04998,0.01602],"object_pos_start":[0.47163,0.04998,0.01602],"object_to_goal_dist_end":0.23659,"object_to_goal_dist_start":0.23659,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8216.0,"raw_peak_contact_force":91.00103,"tcp_end":[0.44845,0.03561,0.20963],"tcp_start":[0.41502,0.01191,0.13356],"tcp_to_object_dist_end":0.19552,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.91892,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19419,"approach_1.speed":0.013,"descend_1.grasp_z_offset":0.00245,"descend_1.speed":0.02748,"lift_1.lift_height":0.16675,"lift_1.speed":0.072,"retract_1.retract_height":0.28248,"retract_1.speed":0.08823,"transport_1.arc_height":0.09745,"transport_1.speed":0.0576},"optimized_scores":{"best_composite_score":-0.47418,"best_fitness_score":0.17582,"best_task_score":0.12365},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.62634,0.00579,-0.00047],"force_p95":194.53449,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1626.09515,"mean_force":201.84137,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38168,0.00528,0.11806]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.63597,0.01021,-0.00031],"force_p95":303.8146,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":404.95065,"mean_force":282.12811,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39682,0.01083,0.13117]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.65011,0.01311,-9e-05],"force_p95":90.23185,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.28139,"mean_force":61.31864,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.40655,0.01384,0.12338]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.64991,0.01304,-0.00014],"force_p95":83.80688,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.16453,"mean_force":71.26264,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40634,0.01371,0.12328]},{"body_a":"grasp_target","body_b":"hand","contact_count":49.0,"contact_point_centroid":[0.46076,0.03211,0.04143],"force_p95":3.54624,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.07608,"mean_force":1.6075,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37688,0.00337,0.06218]},{"body_a":"grasp_target","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.48178,0.02926,0.01751],"force_p95":2.58633,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.11731,"mean_force":0.75391,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36991,0.00331,0.06018]},{"body_a":"world","body_b":"grasp_target","contact_count":3871.0,"contact_point_centroid":[0.44654,0.0488,-0.00215],"force_p95":0.13845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42791,"mean_force":0.14159,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39479,0.00503,0.12856]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4409,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39682,0.01083,0.13117]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4409,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40634,0.01371,0.12328]},{"body_a":"world","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.4409,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42092,0.03083,0.14794]},{"body_a":"left_finger","body_b":"right_finger","contact_count":330.0,"contact_point_centroid":[0.40851,0.01367,0.12216],"force_p95":0.01431,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01142,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40645,0.01368,0.12308]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2410.0,"contact_point_centroid":[0.42286,0.03084,0.14717],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01067,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42094,0.03085,0.14797]},{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.52292,0.00851,-0.00266],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36823,0.00327,0.05415]}],"total_contact_groups":13},"final_pose_error":0.01059,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.4409,0.04873,0.01602],"final_tcp_position":[0.43623,0.04636,0.17358],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1626.09515,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4409,0.04873,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31354,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":194.0396,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4856.0,"raw_peak_contact_force":1626.09515,"subtask_id":"approach_1","tcp_end":[0.38328,0.00774,0.13363],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13723,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4409,0.04873,0.01602],"object_pos_start":[0.4409,0.04873,0.01602],"object_to_goal_dist_end":0.31354,"object_to_goal_dist_start":0.31354,"object_z_max":0.01602,"peak_contact_force":263.41676,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":404.95065,"subtask_id":"descend_1","tcp_end":[0.40585,0.01374,0.12372],"tcp_start":[0.38328,0.00774,0.13363],"tcp_to_object_dist_end":0.11855,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4409,0.04873,0.01602],"object_pos_start":[0.4409,0.04873,0.01602],"object_to_goal_dist_end":0.31354,"object_to_goal_dist_start":0.31354,"object_z_max":0.01602,"peak_contact_force":66.90656,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2580.0,"raw_peak_contact_force":88.16453,"subtask_id":"grasp_1","tcp_end":[0.40645,0.01368,0.12307],"tcp_start":[0.40585,0.01374,0.12372],"tcp_to_object_dist_end":0.1178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":578.0,"n_steps_budget":690.0,"object_pos_end":[0.4409,0.04873,0.01602],"object_pos_start":[0.4409,0.04873,0.01602],"object_to_goal_dist_end":0.31354,"object_to_goal_dist_start":0.31354,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4733.0,"raw_peak_contact_force":92.28139,"tcp_end":[0.43623,0.04636,0.17358],"tcp_start":[0.40645,0.01368,0.12307],"tcp_to_object_dist_end":0.15765,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":7.0,"average_failure_rate":0.07143,"average_mean_iterations":19.56122,"average_solve_count":98.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15643,"approach_1.speed":0.01792,"descend_1.grasp_z_offset":0.04981,"descend_1.speed":0.01553,"lift_1.lift_height":0.17207,"lift_1.speed":0.04101,"retract_1.retract_height":0.31974,"retract_1.speed":0.08572,"transport_1.arc_height":0.10977,"transport_1.speed":0.03603},"optimized_scores":{"best_composite_score":-0.50679,"best_fitness_score":0.14321,"best_task_score":0.10559},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.63292,-0.00252,-0.00047],"force_p95":194.8525,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1638.57974,"mean_force":199.37883,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39164,-0.00254,0.124]},{"body_a":"world","body_b":"link5","contact_count":63.0,"contact_point_centroid":[0.65757,0.09215,-0.00077],"force_p95":502.00562,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":798.32482,"mean_force":328.46095,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48545,-0.04747,0.16064]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.64114,-0.0048,-0.00028],"force_p95":281.60143,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.57401,"mean_force":247.99964,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.41457,-0.00544,0.1519]},{"body_a":"world","body_b":"link6","contact_count":35.0,"contact_point_centroid":[0.65777,-0.00749,-4e-05],"force_p95":305.33742,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":379.28342,"mean_force":117.4127,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4284,-0.00805,0.14817]},{"body_a":"link5","body_b":"hand","contact_count":135.0,"contact_point_centroid":[0.527,0.06273,0.13181],"force_p95":263.76817,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.43688,"mean_force":140.92392,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47844,-0.03824,0.1619]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.65478,-0.0064,-0.00013],"force_p95":77.8625,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.49985,"mean_force":70.87426,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4247,-0.00698,0.14688]},{"body_a":"grasp_target","body_b":"link6","contact_count":630.0,"contact_point_centroid":[0.5325,-0.02376,0.03387],"force_p95":0.47822,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.53322,"mean_force":0.12448,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38983,-0.00224,0.11668]},{"body_a":"grasp_target","body_b":"link7","contact_count":682.0,"contact_point_centroid":[0.52384,-0.01052,0.03299],"force_p95":0.78297,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.30529,"mean_force":0.26746,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39047,-0.00227,0.11651]},{"body_a":"grasp_target","body_b":"hand","contact_count":104.0,"contact_point_centroid":[0.4902,-0.02698,0.04614],"force_p95":2.44245,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.15553,"mean_force":0.92532,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38357,-0.00184,0.08136]},{"body_a":"world","body_b":"grasp_target","contact_count":3723.0,"contact_point_centroid":[0.50673,-0.0263,-0.00234],"force_p95":0.26029,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.03763,"mean_force":0.16002,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40484,-0.00239,0.13543]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50078,-0.02739,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.41457,-0.00544,0.1519]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50078,-0.02739,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4247,-0.00698,0.14688]},{"body_a":"world","body_b":"grasp_target","contact_count":3012.0,"contact_point_centroid":[0.50078,-0.02739,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46232,-0.02399,0.1656]},{"body_a":"left_finger","body_b":"right_finger","contact_count":335.0,"contact_point_centroid":[0.42665,-0.00701,0.1456],"force_p95":0.01397,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01128,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.42477,-0.00701,0.14671]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3231.0,"contact_point_centroid":[0.46466,-0.02411,0.1649],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0129,"mean_force":0.01039,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46266,-0.02417,0.16593]},{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.52985,0.00254,-0.00283],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3747,-0.00186,0.05265]}],"total_contact_groups":16},"final_pose_error":0.10759,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50078,-0.02739,0.01602],"final_tcp_position":[0.51229,-0.03999,0.29432],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1638.57974,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50078,-0.02739,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33723,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":190.46152,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6043.0,"raw_peak_contact_force":1638.57974,"subtask_id":"approach_1","tcp_end":[0.39775,-0.00364,0.14784],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16898,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50078,-0.02739,0.01602],"object_pos_start":[0.50078,-0.02739,0.01602],"object_to_goal_dist_end":0.33723,"object_to_goal_dist_start":0.33723,"object_z_max":0.01602,"peak_contact_force":280.22039,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":383.57401,"subtask_id":"descend_1","tcp_end":[0.4243,-0.00693,0.14729],"tcp_start":[0.39775,-0.00364,0.14784],"tcp_to_object_dist_end":0.1533,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50078,-0.02739,0.01602],"object_pos_start":[0.50078,-0.02739,0.01602],"object_to_goal_dist_end":0.33723,"object_to_goal_dist_start":0.33723,"object_z_max":0.01602,"peak_contact_force":67.90187,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2585.0,"raw_peak_contact_force":84.49985,"subtask_id":"grasp_1","tcp_end":[0.42477,-0.00701,0.14671],"tcp_start":[0.4243,-0.00693,0.14729],"tcp_to_object_dist_end":0.15255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.50078,-0.02739,0.01602],"object_pos_start":[0.50078,-0.02739,0.01602],"object_to_goal_dist_end":0.33723,"object_to_goal_dist_start":0.33723,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6476.0,"raw_peak_contact_force":798.32482,"tcp_end":[0.51229,-0.03999,0.29432],"tcp_start":[0.42477,-0.00701,0.14671],"tcp_to_object_dist_end":0.27882,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```